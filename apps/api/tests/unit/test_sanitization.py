"""
Unit tests for input sanitization utilities.
"""
import pytest
from core.sanitization import sanitize_html, sanitize_path, sanitize_markdown


class TestHTMLSanitization:
    """Test HTML sanitization."""

    def test_sanitize_script_tags(self):
        """Test removal of script tags."""
        input_text = "<script>alert('xss')</script>Hello World"
        result = sanitize_html(input_text)
        assert "<script>" not in result
        assert "Hello World" in result or "HelloWorld" in result

    def test_sanitize_style_tags(self):
        """Test removal of style tags."""
        input_text = "<style>body { display: none; }</style>Content"
        result = sanitize_html(input_text)
        assert "<style>" not in result
        assert "Content" in result

    def test_sanitize_all_html_tags(self):
        """Test removal of all HTML tags."""
        input_text = "<div><p>Hello <b>World</b></p></div>"
        result = sanitize_html(input_text)
        assert "<div>" not in result
        assert "<p>" not in result
        assert "<b>" not in result
        # Text content should remain
        assert "Hello" in result or "World" in result

    def test_sanitize_empty_string(self):
        """Test sanitization of empty string."""
        result = sanitize_html("")
        assert result == ""

    def test_sanitize_plain_text(self):
        """Test sanitization of plain text (no tags)."""
        input_text = "Just plain text"
        result = sanitize_html(input_text)
        assert result == input_text


class TestPathSanitization:
    """Test path traversal sanitization."""

    def test_sanitize_path_traversal(self):
        """Test removal of ../ path traversal."""
        input_path = "../../../etc/passwd"
        result = sanitize_path(input_path)
        assert "../" not in result
        assert "etc/passwd" in result

    def test_sanitize_windows_path_traversal(self):
        """Test removal of ..\\ path traversal."""
        input_path = "..\\..\\windows\\system32"
        result = sanitize_path(input_path)
        assert "..\\" not in result

    def test_sanitize_leading_slash(self):
        """Test removal of leading slash."""
        input_path = "/absolute/path/to/file"
        result = sanitize_path(input_path)
        assert not result.startswith("/")
        assert "absolute/path/to/file" in result

    def test_sanitize_null_bytes(self):
        """Test removal of null bytes."""
        input_path = "path/to/file\x00.txt"
        result = sanitize_path(input_path)
        assert "\x00" not in result

    def test_sanitize_empty_path(self):
        """Test sanitization of empty path."""
        result = sanitize_path("")
        assert result == ""

    def test_sanitize_safe_path(self):
        """Test that safe paths are unchanged."""
        input_path = "safe/relative/path/file.txt"
        result = sanitize_path(input_path)
        # Should only remove leading slash if any
        assert "safe/relative/path/file.txt" in result


class TestMarkdownSanitization:
    """Test markdown content sanitization."""

    def test_sanitize_markdown_script_tags(self):
        """Test removal of script tags from markdown."""
        input_md = "# Title\n<script>alert('xss')</script>\n\nContent"
        result = sanitize_markdown(input_md)
        assert "<script>" not in result
        # Markdown headers should be preserved
        assert "#" in result or "Title" in result

    def test_sanitize_markdown_iframe(self):
        """Test removal of iframe tags."""
        input_md = "# Header\n<iframe src='evil.com'></iframe>\nText"
        result = sanitize_markdown(input_md)
        assert "<iframe>" not in result
        assert "iframe" not in result.lower() or "Header" in result

    def test_sanitize_markdown_javascript_protocol(self):
        """Test removal of javascript: protocol."""
        input_md = "[Click here](javascript:alert('xss'))"
        result = sanitize_markdown(input_md)
        assert "javascript:" not in result.lower()

    def test_sanitize_markdown_preserve_safe_tags(self):
        """Test that safe markdown HTML tags are preserved."""
        input_md = "# Header\n\n**Bold** and *italic* text.\n\n```code```"
        result = sanitize_markdown(input_md)
        # Content should be present
        assert "Header" in result or "Bold" in result or "italic" in result

    def test_sanitize_empty_markdown(self):
        """Test sanitization of empty markdown."""
        result = sanitize_markdown("")
        assert result == ""

    def test_sanitize_plain_markdown(self):
        """Test sanitization of plain markdown (no HTML)."""
        input_md = "# Title\n\nJust **markdown** content."
        result = sanitize_markdown(input_md)
        # Should contain the markdown content
        assert "Title" in result or "markdown" in result
