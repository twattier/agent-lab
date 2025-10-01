"""
Input sanitization utilities for security.
"""
import re
from typing import Optional

try:
    import bleach
except ImportError:
    bleach = None


ALLOWED_TAGS: list = []  # No HTML tags allowed in text fields
ALLOWED_ATTRIBUTES: dict = {}


def sanitize_html(text: str) -> str:
    """
    Strip all HTML and script tags from text input.

    Args:
        text: Input text that may contain HTML

    Returns:
        Sanitized text with all HTML tags removed
    """
    if not text:
        return text

    if bleach is None:
        # Fallback: Remove basic HTML tags using regex
        text = re.sub(r'<[^>]+>', '', text)
        # Remove script content
        text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        # Remove style content
        text = re.sub(r'<style.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        return text.strip()

    return bleach.clean(text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)


def sanitize_path(path: str) -> str:
    """
    Prevent path traversal attacks.

    Args:
        path: File path string

    Returns:
        Sanitized path with traversal patterns removed
    """
    if not path:
        return path

    # Remove ../ and ..\ patterns (path traversal)
    path = re.sub(r'\.\.[/\\]', '', path)
    # Remove leading slashes for relative paths
    path = path.lstrip('/')
    # Remove null bytes
    path = path.replace('\x00', '')

    return path


def sanitize_markdown(content: str) -> str:
    """
    Sanitize markdown content for safe rendering.

    Args:
        content: Markdown content string

    Returns:
        Sanitized markdown with dangerous HTML removed
    """
    if not content:
        return content

    if bleach is None:
        # Fallback: Remove basic dangerous content
        content = re.sub(r'<script.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'<iframe.*?</iframe>', '', content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'javascript:', '', content, flags=re.IGNORECASE)
        return content

    # Allow safe markdown HTML tags
    allowed_tags = [
        'p', 'br', 'strong', 'em', 'code', 'pre', 'ul', 'ol', 'li',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'a', 'hr'
    ]
    allowed_attributes = {
        'a': ['href', 'title'],
        'code': ['class']
    }

    return bleach.clean(content, tags=allowed_tags, attributes=allowed_attributes, strip=True)
