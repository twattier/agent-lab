"""Base LLM provider abstraction layer."""

import asyncio
from abc import ABC, abstractmethod
from typing import Optional

from pydantic import BaseModel


class LLMConfig(BaseModel):
    """LLM provider configuration."""

    provider: str
    api_key: str
    base_url: Optional[str] = None
    model: str
    max_tokens: int = 1000
    temperature: float = 0.7


class LLMProviderError(Exception):
    """Exception for LLM provider errors."""

    def __init__(self, provider: str, message: str, original_error: Optional[Exception] = None):
        """Initialize LLM provider error.

        Args:
            provider: Name of the LLM provider
            message: Error message
            original_error: Original exception that caused this error
        """
        self.provider = provider
        self.message = message
        self.original_error = original_error
        super().__init__(f"[{provider}] {message}")


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, config: LLMConfig):
        """Initialize LLM provider.

        Args:
            config: LLM provider configuration
        """
        self.config = config

    @abstractmethod
    async def generate_completion(self, prompt: str, context: dict) -> str:
        """Generate completion from LLM.

        Args:
            prompt: Prompt text
            context: Additional context for generation

        Returns:
            Generated completion text

        Raises:
            LLMProviderError: If generation fails
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if LLM provider is healthy and accessible.

        Returns:
            True if provider is healthy, False otherwise
        """
        pass


async def retry_with_backoff(
    func,
    max_retries: int = 3,
    base_delay: float = 1.0,
) -> any:
    """Retry function with exponential backoff.

    Args:
        func: Async function to retry
        max_retries: Maximum number of retries
        base_delay: Base delay in seconds (will be doubled each retry)

    Returns:
        Result from successful function call

    Raises:
        Exception: Last exception if all retries fail
    """
    last_exception = None

    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                await asyncio.sleep(delay)

    raise last_exception
