"""OLLAMA LLM provider implementation for local models."""

import os
from typing import Optional

import httpx

from .base_provider import BaseLLMProvider, LLMConfig, LLMProviderError, retry_with_backoff


class OLLAMAProvider(BaseLLMProvider):
    """OLLAMA local LLM provider implementation."""

    def __init__(self, config: Optional[LLMConfig] = None):
        """Initialize OLLAMA provider.

        Args:
            config: Optional LLM configuration. If None, loads from environment.
        """
        if config is None:
            config = LLMConfig(
                provider="ollama",
                api_key="",  # OLLAMA doesn't require API key
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                model=os.getenv("OLLAMA_MODEL", "llama2"),
            )

        super().__init__(config)

    async def generate_completion(self, prompt: str, context: dict) -> str:
        """Generate completion from OLLAMA.

        Args:
            prompt: Prompt text
            context: Additional context for generation

        Returns:
            Generated completion text

        Raises:
            LLMProviderError: If generation fails
        """
        async def _generate():
            try:
                # Build prompt with system context
                system_message = context.get("system", "")
                full_prompt = f"{system_message}\n\n{prompt}" if system_message else prompt

                # Call OLLAMA API
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        f"{self.config.base_url}/api/generate",
                        json={
                            "model": self.config.model,
                            "prompt": full_prompt,
                            "stream": False,
                            "options": {
                                "temperature": self.config.temperature,
                                "num_predict": self.config.max_tokens,
                            },
                        },
                    )

                    # Check response status
                    if response.status_code != 200:
                        raise LLMProviderError(
                            provider="ollama",
                            message=f"OLLAMA API returned status {response.status_code}: {response.text}",
                        )

                    # Parse response
                    result = response.json()
                    return result.get("response", "")

            except httpx.ConnectError as e:
                raise LLMProviderError(
                    provider="ollama",
                    message=f"Failed to connect to OLLAMA at {self.config.base_url}. Is OLLAMA running?",
                    original_error=e,
                )

            except httpx.TimeoutException as e:
                raise LLMProviderError(
                    provider="ollama",
                    message="OLLAMA request timed out",
                    original_error=e,
                )

            except Exception as e:
                raise LLMProviderError(
                    provider="ollama",
                    message=f"Unexpected error: {str(e)}",
                    original_error=e,
                )

        try:
            # Retry with exponential backoff
            return await retry_with_backoff(_generate, max_retries=3, base_delay=1.0)

        except LLMProviderError:
            raise

    async def health_check(self) -> bool:
        """Check if OLLAMA provider is healthy.

        Returns:
            True if provider is healthy and model is available, False otherwise
        """
        try:
            # Check if OLLAMA service is running by listing models
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.config.base_url}/api/tags")

                if response.status_code != 200:
                    return False

                # Check if configured model is available
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]

                # OLLAMA model names can have tags (e.g., "llama2:latest")
                # Check if our model matches any available model
                for model_name in model_names:
                    if self.config.model in model_name or model_name.startswith(self.config.model):
                        return True

                return False

        except httpx.ConnectError:
            # OLLAMA service not running
            return False

        except httpx.TimeoutException:
            # OLLAMA service not responding
            return False

        except Exception:
            # Any other error
            return False
