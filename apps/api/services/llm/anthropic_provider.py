"""Anthropic LLM provider implementation."""

import os
from typing import Optional

import anthropic
from anthropic import Anthropic

from .base_provider import BaseLLMProvider, LLMConfig, LLMProviderError, retry_with_backoff


class AnthropicProvider(BaseLLMProvider):
    """Anthropic (Claude) LLM provider implementation."""

    def __init__(self, config: Optional[LLMConfig] = None):
        """Initialize Anthropic provider.

        Args:
            config: Optional LLM configuration. If None, loads from environment.
        """
        if config is None:
            config = LLMConfig(
                provider="anthropic",
                api_key=os.getenv("ANTHROPIC_API_KEY", ""),
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229"),
            )

        super().__init__(config)

        # Initialize Anthropic client
        self.client = Anthropic(api_key=self.config.api_key)

    async def generate_completion(self, prompt: str, context: dict) -> str:
        """Generate completion from Anthropic.

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
                # Build messages from prompt
                messages = [
                    {"role": "user", "content": prompt}
                ]

                # Get system message from context
                system_message = context.get("system", "You are a helpful assistant.")

                # Call Anthropic API
                response = self.client.messages.create(
                    model=self.config.model,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    system=system_message,
                    messages=messages,
                )

                # Convert Anthropic response format to unified string format
                # Anthropic returns list of content blocks
                return self._extract_text_from_response(response)

            except anthropic.AnthropicError as e:
                raise LLMProviderError(
                    provider="anthropic",
                    message=f"Anthropic API error: {str(e)}",
                    original_error=e,
                )

            except Exception as e:
                raise LLMProviderError(
                    provider="anthropic",
                    message=f"Unexpected error: {str(e)}",
                    original_error=e,
                )

        try:
            # Retry with exponential backoff
            return await retry_with_backoff(_generate, max_retries=3, base_delay=1.0)

        except anthropic.AnthropicError as e:
            raise LLMProviderError(
                provider="anthropic",
                message="API error after retries",
                original_error=e,
            )

    def _extract_text_from_response(self, response) -> str:
        """Extract text from Anthropic response format.

        Anthropic returns messages with content blocks. This method
        extracts and concatenates text from all text blocks.

        Args:
            response: Anthropic API response

        Returns:
            Concatenated text from all content blocks
        """
        text_parts = []
        for content_block in response.content:
            if hasattr(content_block, "text"):
                text_parts.append(content_block.text)

        return "".join(text_parts)

    async def health_check(self) -> bool:
        """Check if Anthropic provider is healthy.

        Returns:
            True if provider is healthy, False otherwise
        """
        try:
            # Send a minimal test request to validate API key
            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}],
            )
            return response is not None

        except anthropic.AnthropicError:
            return False

        except Exception:
            return False
