"""
Embedding generation service for document semantic search.

OpenAI API Usage & Cost Estimation:
-----------------------------------
This service uses OpenAI's text-embedding-ada-002 model for generating semantic embeddings.

Pricing (as of 2024):
- Model: text-embedding-ada-002
- Cost: $0.0001 per 1K tokens (~750 words)
- Dimensions: 1536
- Rate Limit: 3,000 requests/minute (tier 1)

Example Cost Estimates:
- 1,000 documents (avg 500 words each): ~$0.07
- 10,000 documents (avg 500 words each): ~$0.67
- 100,000 documents (avg 500 words each): ~$6.70

Best Practices:
- Batch document creation when possible to reduce API calls
- Monitor usage via OpenAI dashboard
- Set up billing alerts in OpenAI account
- Cache embeddings to avoid regenerating for unchanged content (implemented via content_hash)

Rate Limiting:
- OpenAI enforces rate limits (3K requests/min for tier 1)
- Consider implementing application-level rate limiting for high-volume operations
- Use exponential backoff for retry logic (implemented below)

Environment Setup:
- Set OPENAI_API_KEY environment variable
- Never commit API keys to version control
- Use secrets management in production (e.g., AWS Secrets Manager, HashiCorp Vault)
"""
import os
import asyncio
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings using OpenAI API with retry logic."""

    def __init__(self, api_key: Optional[str] = None, max_retries: int = 3):
        """
        Initialize embedding service.

        Args:
            api_key: OpenAI API key. If None, reads from OPENAI_API_KEY env var.
            max_retries: Maximum number of retry attempts for transient failures (default: 3)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = "text-embedding-ada-002"
        self.dimensions = 1536
        self.max_retries = max_retries

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text using OpenAI API with exponential backoff retry.

        Implements retry logic for transient failures (rate limits, network issues, API timeouts).
        Uses exponential backoff: 1s, 2s, 4s delays between retries.

        Args:
            text: Text to generate embedding for

        Returns:
            List of floats representing the embedding vector (1536 dimensions)

        Raises:
            ValueError: If API key is not configured or embedding dimension mismatch
            ImportError: If OpenAI package not installed
            Exception: If API call fails after all retries
        """
        if not self.api_key:
            raise ValueError("OpenAI API key not configured. Set OPENAI_API_KEY environment variable.")

        try:
            # Import OpenAI client only when needed
            from openai import AsyncOpenAI, RateLimitError, APITimeoutError, APIConnectionError

            client = AsyncOpenAI(api_key=self.api_key)

            # Retry loop with exponential backoff
            last_exception = None
            for attempt in range(self.max_retries):
                try:
                    # Generate embedding
                    response = await client.embeddings.create(
                        input=text,
                        model=self.model
                    )

                    # Extract embedding vector
                    embedding = response.data[0].embedding

                    if len(embedding) != self.dimensions:
                        raise ValueError(f"Expected {self.dimensions} dimensions, got {len(embedding)}")

                    return embedding

                except (RateLimitError, APITimeoutError, APIConnectionError) as e:
                    # Transient errors - retry with exponential backoff
                    last_exception = e
                    if attempt < self.max_retries - 1:
                        backoff_time = 2 ** attempt  # 1s, 2s, 4s
                        logger.warning(
                            f"Transient error on attempt {attempt + 1}/{self.max_retries}: {str(e)}. "
                            f"Retrying in {backoff_time}s..."
                        )
                        await asyncio.sleep(backoff_time)
                    else:
                        logger.error(
                            f"Failed after {self.max_retries} attempts: {str(e)}"
                        )
                        raise

            # If we exhausted retries, raise the last exception
            if last_exception:
                raise last_exception

        except ImportError:
            logger.error("OpenAI package not installed. Install with: pip install openai")
            raise ImportError("OpenAI package required for embedding generation")
        except ValueError as e:
            # Re-raise validation errors without retry
            logger.error(f"Validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise


# Singleton instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """
    Get singleton embedding service instance.

    Returns:
        EmbeddingService instance
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
