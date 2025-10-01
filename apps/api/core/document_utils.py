"""
Document utility functions for hashing and content management.
"""
import hashlib


def generate_content_hash(content: str) -> str:
    """
    Generate SHA-256 hash for document content.

    Args:
        content: The document content to hash

    Returns:
        SHA-256 hash as hexadecimal string (64 characters)
    """
    return hashlib.sha256(content.encode('utf-8')).hexdigest()
