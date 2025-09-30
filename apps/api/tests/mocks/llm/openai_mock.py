"""
Mock OpenAI API Implementation

Provides a mock implementation of the OpenAI API for testing fallback
LLM provider functionality.
"""

from typing import AsyncIterator, Dict, Any, List, Optional
from tests.fixtures.llm.openai_responses import (
    OPENAI_COMPLETION_RESPONSE,
    OPENAI_STREAMING_CHUNK,
    OPENAI_ERROR_RESPONSE,
    OPENAI_FUNCTION_CALL_RESPONSE,
)


class MockOpenAIAPI:
    """
    Mock implementation of OpenAI API for testing.

    Usage:
        >>> mock_openai = MockOpenAIAPI()
        >>> response = await mock_openai.chat.completions.create(
        ...     model="gpt-4",
        ...     messages=[{"role": "user", "content": "Hello"}]
        ... )
    """

    def __init__(self, api_key: str = "test_key", fail_rate: float = 0.0):
        """
        Initialize mock OpenAI API.

        Args:
            api_key: Mock API key (not validated)
            fail_rate: Probability of simulating API errors (0.0 to 1.0)
        """
        self.api_key = api_key
        self.fail_rate = fail_rate
        self.chat = MockChat(fail_rate=fail_rate)


class MockChat:
    """Mock Chat API endpoint."""

    def __init__(self, fail_rate: float = 0.0):
        self.completions = MockCompletions(fail_rate=fail_rate)


class MockCompletions:
    """Mock Completions API endpoint."""

    def __init__(self, fail_rate: float = 0.0):
        self.fail_rate = fail_rate
        self.call_count = 0

    async def create(
        self,
        model: str,
        messages: List[Dict[str, str]],
        stream: bool = False,
        functions: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any] | AsyncIterator[Dict[str, Any]]:
        """
        Mock completion creation.

        Args:
            model: Model identifier
            messages: List of message dictionaries
            stream: Whether to stream the response
            functions: Optional function definitions

        Returns:
            Mock response or async iterator for streaming
        """
        self.call_count += 1

        # Simulate error based on fail_rate
        import random
        if random.random() < self.fail_rate:
            if stream:
                return self._stream_error()
            return OPENAI_ERROR_RESPONSE

        # Return function call response if functions are provided
        if functions:
            return OPENAI_FUNCTION_CALL_RESPONSE

        # Handle streaming vs non-streaming
        if stream:
            return self._stream_response()

        return OPENAI_COMPLETION_RESPONSE

    async def _stream_response(self) -> AsyncIterator[Dict[str, Any]]:
        """Generate mock streaming response."""
        for _ in range(5):
            yield OPENAI_STREAMING_CHUNK

    async def _stream_error(self) -> AsyncIterator[Dict[str, Any]]:
        """Generate mock streaming error."""
        yield OPENAI_ERROR_RESPONSE
