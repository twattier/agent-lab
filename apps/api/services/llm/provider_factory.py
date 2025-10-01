"""LLM Provider Factory for creating and managing LLM providers."""

import logging
import os
from typing import Optional

from .base_provider import BaseLLMProvider, LLMConfig, LLMProviderError
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .ollama_provider import OLLAMAProvider


logger = logging.getLogger(__name__)


class LLMProviderFactory:
    """Factory for creating and managing LLM providers."""

    # Provider registry mapping names to classes
    _PROVIDER_REGISTRY = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "ollama": OLLAMAProvider,
    }

    # Cache of initialized providers
    _providers: dict[str, BaseLLMProvider] = {}

    # Primary and fallback provider configuration
    _primary_provider: Optional[str] = None
    _fallback_providers: list[str] = []

    @classmethod
    def create_provider(cls, provider_name: str, config: Optional[LLMConfig] = None) -> BaseLLMProvider:
        """Create LLM provider instance.

        Args:
            provider_name: Name of provider ('openai', 'anthropic', 'ollama')
            config: Optional provider configuration. If None, loads from environment.

        Returns:
            Initialized LLM provider instance

        Raises:
            ValueError: If provider name is not recognized
        """
        provider_name = provider_name.lower()

        if provider_name not in cls._PROVIDER_REGISTRY:
            raise ValueError(
                f"Unknown provider: {provider_name}. "
                f"Available providers: {', '.join(cls._PROVIDER_REGISTRY.keys())}"
            )

        # Get provider class
        provider_class = cls._PROVIDER_REGISTRY[provider_name]

        # Create provider instance
        provider = provider_class(config)

        # Cache provider
        cls._providers[provider_name] = provider

        return provider

    @classmethod
    async def get_healthy_provider(cls, preferred_provider: Optional[str] = None) -> BaseLLMProvider:
        """Get a healthy provider, with fallback support.

        Args:
            preferred_provider: Preferred provider name. If None, uses primary.

        Returns:
            Healthy LLM provider instance

        Raises:
            LLMProviderError: If no healthy provider is available
        """
        # Determine provider order
        provider_order = []

        if preferred_provider:
            provider_order.append(preferred_provider)
        elif cls._primary_provider:
            provider_order.append(cls._primary_provider)

        provider_order.extend(cls._fallback_providers)

        # Try each provider in order
        for provider_name in provider_order:
            try:
                # Get or create provider
                if provider_name not in cls._providers:
                    cls.create_provider(provider_name)

                provider = cls._providers[provider_name]

                # Check health
                is_healthy = await provider.health_check()
                if is_healthy:
                    logger.info(f"Using healthy provider: {provider_name}")
                    return provider
                else:
                    logger.warning(f"Provider {provider_name} failed health check")

            except Exception as e:
                logger.warning(f"Failed to initialize provider {provider_name}: {str(e)}")

        # No healthy provider found
        raise LLMProviderError(
            provider="factory",
            message="No healthy LLM provider available",
        )

    @classmethod
    async def validate_all_providers(cls) -> dict[str, bool]:
        """Validate health of all configured providers on startup.

        Returns:
            Dictionary mapping provider names to health status
        """
        health_status = {}

        # Load provider configuration from environment
        cls._load_provider_config()

        # Check each configured provider
        for provider_name in cls._PROVIDER_REGISTRY.keys():
            try:
                # Only validate if API key is configured
                if cls._is_provider_configured(provider_name):
                    provider = cls.create_provider(provider_name)
                    is_healthy = await provider.health_check()
                    health_status[provider_name] = is_healthy

                    if is_healthy:
                        logger.info(f"Provider {provider_name} is healthy")
                    else:
                        logger.warning(f"Provider {provider_name} failed health check")
                else:
                    logger.info(f"Provider {provider_name} not configured, skipping validation")
                    health_status[provider_name] = False

            except Exception as e:
                logger.error(f"Failed to validate provider {provider_name}: {str(e)}")
                health_status[provider_name] = False

        return health_status

    @classmethod
    def _load_provider_config(cls):
        """Load provider configuration from environment variables."""
        # Set primary provider (default to OpenAI if available)
        if os.getenv("OPENAI_API_KEY"):
            cls._primary_provider = "openai"
        elif os.getenv("ANTHROPIC_API_KEY"):
            cls._primary_provider = "anthropic"

        # Set fallback providers
        cls._fallback_providers = []
        if os.getenv("ANTHROPIC_API_KEY") and cls._primary_provider != "anthropic":
            cls._fallback_providers.append("anthropic")
        if os.getenv("OPENAI_API_KEY") and cls._primary_provider != "openai":
            cls._fallback_providers.append("openai")

        # OLLAMA is always a fallback (doesn't require API key)
        if cls._is_provider_configured("ollama"):
            cls._fallback_providers.append("ollama")

    @classmethod
    def _is_provider_configured(cls, provider_name: str) -> bool:
        """Check if provider is configured.

        Args:
            provider_name: Name of provider to check

        Returns:
            True if provider has required configuration
        """
        if provider_name == "openai":
            return bool(os.getenv("OPENAI_API_KEY"))
        elif provider_name == "anthropic":
            return bool(os.getenv("ANTHROPIC_API_KEY"))
        elif provider_name == "ollama":
            # OLLAMA is considered configured if base URL is set or default is accessible
            return True
        return False
