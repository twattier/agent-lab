"""OpenAI LLM provider implementation."""

import os
from typing import Optional

import openai
from openai import OpenAI

from .base_provider import BaseLLMProvider, LLMConfig, LLMProviderError, retry_with_backoff


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider implementation."""

    def __init__(self, config: Optional[LLMConfig] = None):
        """Initialize OpenAI provider.

        Args:
            config: Optional LLM configuration. If None, loads from environment.
        """
        if config is None:
            config = LLMConfig(
                provider="openai",
                api_key=os.getenv("OPENAI_API_KEY", ""),
                model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
            )

        super().__init__(config)

        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.config.api_key)

    async def generate_completion(self, prompt: str, context: dict) -> str:
        """Generate completion from OpenAI.

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
                # Build messages from prompt and context
                messages = [
                    {"role": "system", "content": context.get("system", "You are a helpful assistant.")},
                    {"role": "user", "content": prompt}
                ]

                # Call OpenAI API
                response = self.client.chat.completions.create(
                    model=self.config.model,
                    messages=messages,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                )

                # Extract completion text
                return response.choices[0].message.content

            except openai.RateLimitError as e:
                # Re-raise rate limit errors for retry logic
                raise e

            except openai.OpenAIError as e:
                raise LLMProviderError(
                    provider="openai",
                    message=f"OpenAI API error: {str(e)}",
                    original_error=e,
                )

            except Exception as e:
                raise LLMProviderError(
                    provider="openai",
                    message=f"Unexpected error: {str(e)}",
                    original_error=e,
                )

        try:
            # Retry with exponential backoff for rate limits
            return await retry_with_backoff(_generate, max_retries=3, base_delay=1.0)

        except openai.RateLimitError as e:
            raise LLMProviderError(
                provider="openai",
                message="Rate limit exceeded after retries",
                original_error=e,
            )

    async def health_check(self) -> bool:
        """Check if OpenAI provider is healthy.

        Returns:
            True if provider is healthy, False otherwise
        """
        try:
            # Attempt to retrieve model information
            self.client.models.retrieve(self.config.model)
            return True

        except openai.OpenAIError:
            return False

        except Exception:
            return False
