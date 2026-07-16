"""Tests for mcp-web-scraper utility functions."""

import pytest
from utils import is_valid_url, format_markdown_table, truncate_text, get_default_headers


class TestIsValidURL:
    """Tests for is_valid_url function."""

    def test_valid_http_url(self):
        """Test a valid HTTP URL."""
        assert is_valid_url("http://example.com") is True

    def test_valid_https_url(self):
        """Test a valid HTTPS URL."""
        assert is_valid_url("https://www.example.com/path?q=1") is True

    def test_invalid_url_no_scheme(self):
        """Test that URL without scheme is invalid."""
        assert is_valid_url("example.com") is False

    def test_invalid_url_empty(self):
        """Test that empty string is invalid."""
        assert is_valid_url("") is False

    def test_valid_url_with_port(self):
        """Test URL with port number."""
        assert is_valid_url("https://example.com:8080/path") is True

    def test_invalid_url_gibberish(self):
        """Test that random string is not a valid URL."""
        assert is_valid_url("not a url at all") is False


class TestFormatMarkdownTable:
    """Tests for format_markdown_table function."""

    def test_basic_table(self):
        """Test formatting a basic table."""
        headers = ["Name", "Value"]
        rows = [["A", "1"], ["B", "2"]]
        result = format_markdown_table(headers, rows)
        assert "| Name | Value |" in result
        assert "| --- | --- |" in result
        assert "| A | 1 |" in result
        assert "| B | 2 |" in result

    def test_empty_headers(self):
        """Test that empty headers returns empty string."""
        result = format_markdown_table([], [])
        assert result == ""

    def test_single_row(self):
        """Test table with a single row."""
        result = format_markdown_table(["Col"], [["data"]])
        assert "| Col |" in result
        assert "| --- |" in result
        assert "| data |" in result

    def test_pipe_escaping(self):
        """Test that pipe characters in cells are escaped."""
        result = format_markdown_table(["Col"], [["a|b"]])
        assert "a\\|b" in result


class TestTruncateText:
    """Tests for truncate_text function."""

    def test_short_text_not_truncated(self):
        """Test that short text is not truncated."""
        text = "Hello world"
        result = truncate_text(text)
        assert result == text

    def test_long_text_truncated(self):
        """Test that text exceeding max_length is truncated."""
        text = "x" * 60000
        result = truncate_text(text, max_length=100)
        assert len(result) < len(text)
        assert "已截断" in result

    def test_custom_max_length(self):
        """Test with custom max_length."""
        text = "Hello, this is a test."
        result = truncate_text(text, max_length=10)
        assert len(result) > 10  # includes truncation notice
        assert result.startswith("Hello, thi")

    def test_exact_length(self):
        """Test text at exact max length is not truncated."""
        text = "x" * 50
        result = truncate_text(text, max_length=50)
        assert result == text


class TestGetDefaultHeaders:
    """Tests for get_default_headers function."""

    def test_returns_dict(self):
        """Test that function returns a dictionary."""
        headers = get_default_headers()
        assert isinstance(headers, dict)

    def test_contains_user_agent(self):
        """Test that headers contain User-Agent."""
        headers = get_default_headers()
        assert "User-Agent" in headers
        assert "Mozilla" in headers["User-Agent"]

    def test_contains_accept(self):
        """Test that headers contain Accept."""
        headers = get_default_headers()
        assert "Accept" in headers
