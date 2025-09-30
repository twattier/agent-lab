"""
OpenAI API mock response fixtures

Provides realistic OpenAI API response structures for testing fallback
LLM provider functionality.
"""

OPENAI_COMPLETION_RESPONSE = {
    "id": "chatcmpl-123ABC",
    "object": "chat.completion",
    "created": 1677652288,
    "model": "gpt-4",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "This is a mock OpenAI API response for testing purposes."
            },
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 10,
        "completion_tokens": 15,
        "total_tokens": 25
    }
}

OPENAI_STREAMING_CHUNK = {
    "id": "chatcmpl-123ABC",
    "object": "chat.completion.chunk",
    "created": 1677652288,
    "model": "gpt-4",
    "choices": [
        {
            "index": 0,
            "delta": {
                "role": "assistant",
                "content": "This is "
            },
            "finish_reason": None
        }
    ]
}

OPENAI_ERROR_RESPONSE = {
    "error": {
        "message": "Rate limit exceeded",
        "type": "rate_limit_error",
        "param": None,
        "code": "rate_limit_exceeded"
    }
}

OPENAI_FUNCTION_CALL_RESPONSE = {
    "id": "chatcmpl-123ABC",
    "object": "chat.completion",
    "created": 1677652288,
    "model": "gpt-4",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": None,
                "function_call": {
                    "name": "execute_task",
                    "arguments": '{"task_name": "implement_feature", "parameters": {}}'
                }
            },
            "finish_reason": "function_call"
        }
    ],
    "usage": {
        "prompt_tokens": 25,
        "completion_tokens": 30,
        "total_tokens": 55
    }
}
