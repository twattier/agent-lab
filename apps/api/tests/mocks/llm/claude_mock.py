"""
Mock Claude API Implementation

Provides a mock implementation of the Anthropic Claude API for testing
without making actual API calls or requiring valid API keys.
"""

from typing import AsyncIterator, Dict, Any, List, Optional
from tests.fixtures.llm.claude_responses import (
    CLAUDE_COMPLETION_RESPONSE,
    CLAUDE_STREAMING_CHUNK_START,
    CLAUDE_STREAMING_CHUNK_DELTA,
    CLAUDE_STREAMING_CHUNK_END,
    CLAUDE_ERROR_RESPONSE,
    CLAUDE_TOOL_USE_RESPONSE,
)


class MockClaudeAPI:
    """
    Mock implementation of Claude API for testing.

    Usage:
        >>> mock_claude = MockClaudeAPI()
        >>> response = await mock_claude.messages.create(
        ...     model="claude-sonnet-4-5-20250929",
        ...     max_tokens=1024,
        ...     messages=[{"role": "user", "content": "Hello"}]
        ... )
    """

    def __init__(self, api_key: str = "test_key", fail_rate: float = 0.0):
        """
        Initialize mock Claude API.

        Args:
            api_key: Mock API key (not validated)
            fail_rate: Probability of simulating API errors (0.0 to 1.0)
        """
        self.api_key = api_key
        self.fail_rate = fail_rate
        self.messages = MockMessages(fail_rate=fail_rate)


class MockMessages:
    """Mock Messages API endpoint."""

    def __init__(self, fail_rate: float = 0.0):
        self.fail_rate = fail_rate
        self.call_count = 0

    async def create(
        self,
        model: str,
        max_tokens: int,
        messages: List[Dict[str, str]],
        stream: bool = False,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any] | AsyncIterator[Dict[str, Any]]:
        """
        Mock message creation.

        Args:
            model: Model identifier
            max_tokens: Maximum tokens to generate
            messages: List of message dictionaries
            stream: Whether to stream the response
            tools: Optional tool definitions

        Returns:
            Mock response or async iterator for streaming
        """
        self.call_count += 1

        # Simulate error based on fail_rate
        import random
        if random.random() < self.fail_rate:
            if stream:
                return self._stream_error()
            return CLAUDE_ERROR_RESPONSE

        # Return tool use response if tools are provided
        if tools:
            return CLAUDE_TOOL_USE_RESPONSE

        # Handle streaming vs non-streaming
        if stream:
            return self._stream_response()

        return CLAUDE_COMPLETION_RESPONSE

    async def _stream_response(self) -> AsyncIterator[Dict[str, Any]]:
        """Generate mock streaming response."""
        yield CLAUDE_STREAMING_CHUNK_START
        yield CLAUDE_STREAMING_CHUNK_DELTA
        yield CLAUDE_STREAMING_CHUNK_DELTA
        yield CLAUDE_STREAMING_CHUNK_END

    async def _stream_error(self) -> AsyncIterator[Dict[str, Any]]:
        """Generate mock streaming error."""
        yield CLAUDE_ERROR_RESPONSE
