"""
Claude API mock response fixtures

Provides realistic Claude API response structures for testing without
making actual API calls to Anthropic services.
"""

CLAUDE_COMPLETION_RESPONSE = {
    "id": "msg_01XYZ123ABC",
    "type": "message",
    "role": "assistant",
    "content": [
        {
            "type": "text",
            "text": "This is a mock Claude API response for testing purposes."
        }
    ],
    "model": "claude-sonnet-4-5-20250929",
    "stop_reason": "end_turn",
    "stop_sequence": None,
    "usage": {
        "input_tokens": 10,
        "output_tokens": 15
    }
}

CLAUDE_STREAMING_CHUNK_START = {
    "type": "message_start",
    "message": {
        "id": "msg_01XYZ123ABC",
        "type": "message",
        "role": "assistant",
        "content": [],
        "model": "claude-sonnet-4-5-20250929",
        "stop_reason": None,
        "stop_sequence": None,
        "usage": {
            "input_tokens": 10,
            "output_tokens": 0
        }
    }
}

CLAUDE_STREAMING_CHUNK_DELTA = {
    "type": "content_block_delta",
    "index": 0,
    "delta": {
        "type": "text_delta",
        "text": "This is "
    }
}

CLAUDE_STREAMING_CHUNK_END = {
    "type": "message_delta",
    "delta": {
        "stop_reason": "end_turn",
        "stop_sequence": None
    },
    "usage": {
        "output_tokens": 15
    }
}

CLAUDE_ERROR_RESPONSE = {
    "type": "error",
    "error": {
        "type": "rate_limit_error",
        "message": "Rate limit exceeded. Please try again later."
    }
}

CLAUDE_TOOL_USE_RESPONSE = {
    "id": "msg_01XYZ123ABC",
    "type": "message",
    "role": "assistant",
    "content": [
        {
            "type": "tool_use",
            "id": "tool_01ABC",
            "name": "execute_task",
            "input": {
                "task_name": "implement_feature",
                "parameters": {}
            }
        }
    ],
    "model": "claude-sonnet-4-5-20250929",
    "stop_reason": "tool_use",
    "stop_sequence": None,
    "usage": {
        "input_tokens": 25,
        "output_tokens": 30
    }
}
