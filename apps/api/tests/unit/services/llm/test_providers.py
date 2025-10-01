"""Unit tests for LLM providers."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
import openai
import anthropic

from services.llm.base_provider import LLMConfig, LLMProviderError
from services.llm.openai_provider import OpenAIProvider
from services.llm.anthropic_provider import AnthropicProvider
from services.llm.ollama_provider import OLLAMAProvider
from services.llm.provider_factory import LLMProviderFactory


@pytest.fixture
def openai_config():
    """Fixture for OpenAI configuration."""
    return LLMConfig(
        provider="openai",
        api_key="test-openai-key",
        model="gpt-4-turbo-preview",
    )


@pytest.fixture
def anthropic_config():
    """Fixture for Anthropic configuration."""
    return LLMConfig(
        provider="anthropic",
        api_key="test-anthropic-key",
        model="claude-3-opus-20240229",
    )


@pytest.fixture
def ollama_config():
    """Fixture for OLLAMA configuration."""
    return LLMConfig(
        provider="ollama",
        api_key="",
        base_url="http://localhost:11434",
        model="llama2",
    )


class TestOpenAIProvider:
    """Tests for OpenAIProvider."""

    @pytest.mark.asyncio
    async def test_generate_completion_success(self, openai_config):
        """Test successful completion generation."""
        provider = OpenAIProvider(openai_config)

        # Mock OpenAI client response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response"))]

        with patch.object(provider.client.chat.completions, "create", return_value=mock_response):
            result = await provider.generate_completion("Test prompt", {"system": "Test system"})

            assert result == "Test response"

    @pytest.mark.asyncio
    async def test_generate_completion_api_error(self, openai_config):
        """Test handling of OpenAI API errors."""
        provider = OpenAIProvider(openai_config)

        with patch.object(
            provider.client.chat.completions,
            "create",
            side_effect=openai.APIError("API error", request=Mock(), body=None),
        ):
            with pytest.raises(LLMProviderError):
                await provider.generate_completion("Test prompt", {})

    @pytest.mark.asyncio
    async def test_generate_completion_rate_limit(self, openai_config):
        """Test retry logic for rate limit errors."""
        provider = OpenAIProvider(openai_config)

        # Mock rate limit error then success
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Success after retry"))]

        with patch.object(
            provider.client.chat.completions,
            "create",
            side_effect=[
                openai.RateLimitError("Rate limit", response=Mock(), body=None),
                mock_response,
            ],
        ):
            result = await provider.generate_completion("Test prompt", {})
            assert result == "Success after retry"

    @pytest.mark.asyncio
    async def test_health_check_success(self, openai_config):
        """Test successful health check."""
        provider = OpenAIProvider(openai_config)

        with patch.object(provider.client.models, "retrieve", return_value=Mock()):
            result = await provider.health_check()
            assert result is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self, openai_config):
        """Test failed health check."""
        provider = OpenAIProvider(openai_config)

        with patch.object(
            provider.client.models,
            "retrieve",
            side_effect=openai.APIError("API error", request=Mock(), body=None),
        ):
            result = await provider.health_check()
            assert result is False


class TestAnthropicProvider:
    """Tests for AnthropicProvider."""

    @pytest.mark.asyncio
    async def test_generate_completion_success(self, anthropic_config):
        """Test successful completion generation."""
        provider = AnthropicProvider(anthropic_config)

        # Mock Anthropic client response
        mock_content = Mock()
        mock_content.text = "Test response"
        mock_response = Mock()
        mock_response.content = [mock_content]

        with patch.object(provider.client.messages, "create", return_value=mock_response):
            result = await provider.generate_completion("Test prompt", {"system": "Test system"})

            assert result == "Test response"

    @pytest.mark.asyncio
    async def test_generate_completion_api_error(self, anthropic_config):
        """Test handling of Anthropic API errors."""
        provider = AnthropicProvider(anthropic_config)

        with patch.object(
            provider.client.messages,
            "create",
            side_effect=anthropic.APIError("API error", request=Mock(), body=None),
        ):
            with pytest.raises(LLMProviderError):
                await provider.generate_completion("Test prompt", {})

    @pytest.mark.asyncio
    async def test_response_format_conversion(self, anthropic_config):
        """Test conversion of Anthropic response format."""
        provider = AnthropicProvider(anthropic_config)

        # Mock multiple content blocks
        mock_content1 = Mock()
        mock_content1.text = "Part 1"
        mock_content2 = Mock()
        mock_content2.text = " Part 2"

        mock_response = Mock()
        mock_response.content = [mock_content1, mock_content2]

        result = provider._extract_text_from_response(mock_response)
        assert result == "Part 1 Part 2"

    @pytest.mark.asyncio
    async def test_health_check_success(self, anthropic_config):
        """Test successful health check."""
        provider = AnthropicProvider(anthropic_config)

        mock_response = Mock()

        with patch.object(provider.client.messages, "create", return_value=mock_response):
            result = await provider.health_check()
            assert result is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self, anthropic_config):
        """Test failed health check."""
        provider = AnthropicProvider(anthropic_config)

        with patch.object(
            provider.client.messages,
            "create",
            side_effect=anthropic.APIError("API error", request=Mock(), body=None),
        ):
            result = await provider.health_check()
            assert result is False


class TestOLLAMAProvider:
    """Tests for OLLAMAProvider."""

    @pytest.mark.asyncio
    async def test_generate_completion_success(self, ollama_config):
        """Test successful completion generation."""
        provider = OLLAMAProvider(ollama_config)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Test OLLAMA response"}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await provider.generate_completion("Test prompt", {})
            assert result == "Test OLLAMA response"

    @pytest.mark.asyncio
    async def test_generate_completion_connection_error(self, ollama_config):
        """Test handling of OLLAMA connection errors."""
        import httpx

        provider = OLLAMAProvider(ollama_config)

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value.post.side_effect = httpx.ConnectError("Connection failed")
            mock_client_class.return_value = mock_client

            with pytest.raises(LLMProviderError, match="Failed to connect"):
                await provider.generate_completion("Test prompt", {})

    @pytest.mark.asyncio
    async def test_generate_completion_timeout(self, ollama_config):
        """Test handling of OLLAMA timeout."""
        import httpx

        provider = OLLAMAProvider(ollama_config)

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value.post.side_effect = httpx.TimeoutException("Timeout")
            mock_client_class.return_value = mock_client

            with pytest.raises(LLMProviderError, match="timed out"):
                await provider.generate_completion("Test prompt", {})

    @pytest.mark.asyncio
    async def test_health_check_success(self, ollama_config):
        """Test successful health check."""
        provider = OLLAMAProvider(ollama_config)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [{"name": "llama2:latest"}, {"name": "codellama:latest"}]
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await provider.health_check()
            assert result is True

    @pytest.mark.asyncio
    async def test_health_check_model_not_available(self, ollama_config):
        """Test health check when model not available."""
        provider = OLLAMAProvider(ollama_config)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [{"name": "different-model:latest"}]
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await provider.health_check()
            assert result is False


class TestLLMProviderFactory:
    """Tests for LLMProviderFactory."""

    def test_create_openai_provider(self, openai_config):
        """Test creating OpenAI provider."""
        provider = LLMProviderFactory.create_provider("openai", openai_config)

        assert isinstance(provider, OpenAIProvider)
        assert provider.config.provider == "openai"

    def test_create_anthropic_provider(self, anthropic_config):
        """Test creating Anthropic provider."""
        provider = LLMProviderFactory.create_provider("anthropic", anthropic_config)

        assert isinstance(provider, AnthropicProvider)
        assert provider.config.provider == "anthropic"

    def test_create_ollama_provider(self, ollama_config):
        """Test creating OLLAMA provider."""
        provider = LLMProviderFactory.create_provider("ollama", ollama_config)

        assert isinstance(provider, OLLAMAProvider)
        assert provider.config.provider == "ollama"

    def test_create_invalid_provider(self):
        """Test creating invalid provider raises ValueError."""
        with pytest.raises(ValueError, match="Unknown provider"):
            LLMProviderFactory.create_provider("invalid")

    @pytest.mark.asyncio
    async def test_get_healthy_provider_fallback(self):
        """Test fallback to secondary provider when primary fails."""
        # Clear cached providers
        LLMProviderFactory._providers = {}
        LLMProviderFactory._primary_provider = "openai"
        LLMProviderFactory._fallback_providers = ["anthropic"]

        # Mock OpenAI failing, Anthropic succeeding
        with patch.object(LLMProviderFactory, "create_provider") as mock_create:
            mock_openai = Mock()
            mock_openai.health_check = AsyncMock(return_value=False)

            mock_anthropic = Mock()
            mock_anthropic.health_check = AsyncMock(return_value=True)

            mock_create.side_effect = [mock_openai, mock_anthropic]

            provider = await LLMProviderFactory.get_healthy_provider()
            assert provider == mock_anthropic
