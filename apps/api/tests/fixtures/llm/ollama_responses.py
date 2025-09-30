"""
OLLAMA API mock response fixtures

Provides realistic OLLAMA local LLM response structures for testing
offline development scenarios.
"""

OLLAMA_COMPLETION_RESPONSE = {
    "model": "llama2",
    "created_at": "2023-08-04T19:22:45.499127Z",
    "response": "This is a mock OLLAMA response for testing purposes.",
    "done": True,
    "context": [1, 2, 3],
    "total_duration": 5589157167,
    "load_duration": 3013701500,
    "prompt_eval_count": 10,
    "prompt_eval_duration": 2180000000,
    "eval_count": 15,
    "eval_duration": 2395000000
}

OLLAMA_STREAMING_CHUNK = {
    "model": "llama2",
    "created_at": "2023-08-04T19:22:45.499127Z",
    "response": "This is ",
    "done": False
}

OLLAMA_STREAMING_FINAL = {
    "model": "llama2",
    "created_at": "2023-08-04T19:22:45.499127Z",
    "response": "",
    "done": True,
    "context": [1, 2, 3],
    "total_duration": 5589157167,
    "load_duration": 3013701500,
    "prompt_eval_count": 10,
    "prompt_eval_duration": 2180000000,
    "eval_count": 15,
    "eval_duration": 2395000000
}

OLLAMA_ERROR_RESPONSE = {
    "error": "model not found"
}

OLLAMA_MODEL_LIST_RESPONSE = {
    "models": [
        {
            "name": "llama2",
            "modified_at": "2023-08-04T19:22:45.499127Z",
            "size": 3825819519,
            "digest": "abc123def456"
        }
    ]
}
