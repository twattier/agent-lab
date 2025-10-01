"""
Unit tests for document utility functions.
"""
import pytest
from core.document_utils import generate_content_hash


def test_generate_content_hash_returns_sha256():
    """Test that generate_content_hash returns a 64-character SHA-256 hash."""
    content = "Test content for hashing"
    hash_value = generate_content_hash(content)

    assert isinstance(hash_value, str)
    assert len(hash_value) == 64
    # Verify it's a valid hex string
    assert all(c in '0123456789abcdef' for c in hash_value)


def test_generate_content_hash_consistency():
    """Test that same content produces same hash."""
    content = "Consistent content"
    hash1 = generate_content_hash(content)
    hash2 = generate_content_hash(content)

    assert hash1 == hash2


def test_generate_content_hash_different_for_different_content():
    """Test that different content produces different hashes."""
    content1 = "Content version 1"
    content2 = "Content version 2"

    hash1 = generate_content_hash(content1)
    hash2 = generate_content_hash(content2)

    assert hash1 != hash2


def test_generate_content_hash_empty_string():
    """Test hash generation for empty string."""
    hash_value = generate_content_hash("")

    assert isinstance(hash_value, str)
    assert len(hash_value) == 64


def test_generate_content_hash_unicode():
    """Test hash generation for Unicode content."""
    content = "Contenu en français avec des caractères spéciaux: éàùç"
    hash_value = generate_content_hash(content)

    assert isinstance(hash_value, str)
    assert len(hash_value) == 64


def test_generate_content_hash_multiline():
    """Test hash generation for multiline content."""
    content = """
    This is a multiline
    document with several
    lines of content.
    """
    hash_value = generate_content_hash(content)

    assert isinstance(hash_value, str)
    assert len(hash_value) == 64
