"""
Mock OLLAMA API Implementation

Provides a mock implementation of the OLLAMA local LLM API for testing
offline development scenarios.
"""

from typing import AsyncIterator, Dict, Any, List
from tests.fixtures.llm.ollama_responses import (
    OLLAMA_COMPLETION_RESPONSE,
    OLLAMA_STREAMING_CHUNK,
    OLLAMA_STREAMING_FINAL,
    OLLAMA_ERROR_RESPONSE,
    OLLAMA_MODEL_LIST_RESPONSE,
)


class MockOllamaAPI:
    """
    Mock implementation of OLLAMA API for testing.

    Usage:
        >>> mock_ollama = MockOllamaAPI()
        >>> response = await mock_ollama.generate(
        ...     model="llama2",
        ...     prompt="Hello"
        ... )
    """

    def __init__(self, host: str = "http://localhost:11434", fail_rate: float = 0.0):
        """
        Initialize mock OLLAMA API.

        Args:
            host: Mock host URL (not actually used)
            fail_rate: Probability of simulating API errors (0.0 to 1.0)
        """
        self.host = host
        self.fail_rate = fail_rate
        self.call_count = 0

    async def generate(
        self,
        model: str,
        prompt: str,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any] | AsyncIterator[Dict[str, Any]]:
        """
        Mock text generation.

        Args:
            model: Model identifier
            prompt: Input prompt
            stream: Whether to stream the response

        Returns:
            Mock response or async iterator for streaming
        """
        self.call_count += 1

        # Simulate error based on fail_rate
        import random
        if random.random() < self.fail_rate:
            if stream:
                return self._stream_error()
            return OLLAMA_ERROR_RESPONSE

        # Handle streaming vs non-streaming
        if stream:
            return self._stream_response()

        return OLLAMA_COMPLETION_RESPONSE

    async def list_models(self) -> Dict[str, Any]:
        """Mock list available models."""
        return OLLAMA_MODEL_LIST_RESPONSE

    async def _stream_response(self) -> AsyncIterator[Dict[str, Any]]:
        """Generate mock streaming response."""
        for _ in range(5):
            yield OLLAMA_STREAMING_CHUNK
        yield OLLAMA_STREAMING_FINAL

    async def _stream_error(self) -> AsyncIterator[Dict[str, Any]]:
        """Generate mock streaming error."""
        yield OLLAMA_ERROR_RESPONSE
