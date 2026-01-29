import pytest

from app.models.schemas import ClassifyRequest, sanitize_text


class TestSanitizeText:
    """Tests for the sanitize_text function"""

    def test_removes_null_characters(self):
        """Test that null characters are removed"""
        text = "Hello\x00World"
        result = sanitize_text(text)
        assert "\x00" not in result
        assert result == "HelloWorld"

    def test_removes_control_characters(self):
        """Test that control characters (except newline/tab) are removed"""
        text = "Test\x01\x02\x03\x04\x05text"
        result = sanitize_text(text)
        assert result == "Testtext"

    def test_preserves_newlines(self):
        """Test that newlines are preserved"""
        text = "Line one\nLine two"
        result = sanitize_text(text)
        assert "\n" in result

    def test_normalizes_multiple_spaces(self):
        """Test that multiple spaces become single space"""
        text = "Word    with    spaces"
        result = sanitize_text(text)
        assert result == "Word with spaces"

    def test_normalizes_multiple_newlines(self):
        """Test that 3+ newlines become double newline"""
        text = "Para one\n\n\n\n\nPara two"
        result = sanitize_text(text)
        assert result == "Para one\n\nPara two"

    def test_strips_whitespace(self):
        """Test that leading/trailing whitespace is stripped"""
        text = "   hello world   "
        result = sanitize_text(text)
        assert result == "hello world"

    def test_handles_tabs(self):
        """Test that tabs are converted to spaces"""
        text = "Word\t\twith\ttabs"
        result = sanitize_text(text)
        assert "\t" not in result
        assert result == "Word with tabs"

    def test_empty_string(self):
        """Test that empty string returns empty"""
        result = sanitize_text("")
        assert result == ""

    def test_whitespace_only(self):
        """Test that whitespace-only returns empty"""
        result = sanitize_text("   \t\n   ")
        assert result == ""


class TestClassifyRequestValidation:
    """Tests for ClassifyRequest Pydantic model validation"""

    def test_valid_text_accepted(self):
        """Test that valid text is accepted"""
        request = ClassifyRequest(text="This is valid political text for analysis.")
        assert request.text == "This is valid political text for analysis."

    def test_text_is_sanitized(self):
        """Test that text is automatically sanitized"""
        request = ClassifyRequest(text="  Text with   extra   spaces  ")
        assert request.text == "Text with extra spaces"

    def test_minimum_length_enforced(self):
        """Test that text below minimum length is rejected"""
        with pytest.raises(ValueError):
            ClassifyRequest(text="short")

    def test_empty_text_rejected(self):
        """Test that empty text is rejected"""
        with pytest.raises(ValueError):
            ClassifyRequest(text="")

    def test_whitespace_only_rejected(self):
        """Test that whitespace-only text is rejected after sanitization"""
        with pytest.raises(ValueError):
            ClassifyRequest(text="     \n\t    ")

    def test_text_with_control_chars_sanitized(self):
        """Test that text with control characters is sanitized"""
        request = ClassifyRequest(text="This has\x00null\x00characters in it")
        assert "\x00" not in request.text

    def test_non_string_rejected(self):
        """Test that non-string values are rejected"""
        with pytest.raises(ValueError):
            ClassifyRequest(text=12345)  # type: ignore
