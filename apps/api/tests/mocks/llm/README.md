# Mock LLM Provider Services

This directory contains mock implementations of various LLM providers for testing purposes.

## Available Mocks

### Claude API Mock (`claude_mock.py`)

Mock implementation of Anthropic's Claude API.

```python
from tests.mocks.llm import MockClaudeAPI

# Basic usage
mock_claude = MockClaudeAPI()
response = await mock_claude.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}]
)

# Simulate errors
mock_claude_with_errors = MockClaudeAPI(fail_rate=0.5)  # 50% error rate

# Streaming
response = await mock_claude.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
    stream=True
)
async for chunk in response:
    print(chunk)
```

### OpenAI API Mock (`openai_mock.py`)

Mock implementation of OpenAI's API for fallback provider testing.

```python
from tests.mocks.llm import MockOpenAIAPI

# Basic usage
mock_openai = MockOpenAIAPI()
response = await mock_openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)

# Function calling
response = await mock_openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Execute task"}],
    functions=[{"name": "execute_task", "parameters": {}}]
)
```

### OLLAMA API Mock (`ollama_mock.py`)

Mock implementation of OLLAMA local LLM API for offline development.

```python
from tests.mocks.llm import MockOllamaAPI

# Basic usage
mock_ollama = MockOllamaAPI()
response = await mock_ollama.generate(
    model="llama2",
    prompt="Hello"
)

# List models
models = await mock_ollama.list_models()

# Streaming
response = await mock_ollama.generate(
    model="llama2",
    prompt="Hello",
    stream=True
)
async for chunk in response:
    print(chunk)
```

## Response Fixtures

Pre-defined response fixtures are available in `tests/fixtures/llm/`:

- `claude_responses.py` - Claude API response structures
- `openai_responses.py` - OpenAI API response structures
- `ollama_responses.py` - OLLAMA API response structures

## Testing Patterns

### Testing with Pytest

```python
import pytest
from tests.mocks.llm import MockClaudeAPI

@pytest.fixture
def mock_llm():
    return MockClaudeAPI()

@pytest.mark.asyncio
async def test_llm_integration(mock_llm):
    response = await mock_llm.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=100,
        messages=[{"role": "user", "content": "Test"}]
    )
    assert response["type"] == "message"
    assert response["role"] == "assistant"
```

### Testing Error Scenarios

```python
@pytest.mark.asyncio
async def test_llm_error_handling():
    mock_llm = MockClaudeAPI(fail_rate=1.0)  # Always fail
    response = await mock_llm.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=100,
        messages=[{"role": "user", "content": "Test"}]
    )
    assert response["type"] == "error"
```

## Benefits

1. **No API Keys Required** - Tests run without real credentials
2. **Fast Execution** - No network latency or rate limits
3. **Predictable Responses** - Consistent test results
4. **Error Simulation** - Test error handling with `fail_rate` parameter
5. **Offline Development** - Work without internet connectivity
