import io

import pytest
from fastapi import HTTPException, UploadFile

from app.models.schemas import FileType
from app.services.file_extractor import FileExtractor, get_file_extractor


class TestFileTypeDetection:
    """Tests for file type detection"""

    def test_detect_txt_file(self):
        """Should detect .txt file type"""
        extractor = get_file_extractor()
        file_type = extractor.get_file_type("document.txt", "text/plain")
        assert file_type.value == "txt"

    def test_detect_pdf_file(self):
        """Should detect .pdf file type"""
        extractor = get_file_extractor()
        file_type = extractor.get_file_type("document.pdf", "application/pdf")
        assert file_type.value == "pdf"

    def test_detect_docx_file(self):
        """Should detect .docx file type"""
        extractor = get_file_extractor()
        mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        file_type = extractor.get_file_type("document.docx", mime)
        assert file_type.value == "docx"

    def test_unsupported_extension(self):
        """Should reject unsupported file extensions"""
        extractor = get_file_extractor()
        with pytest.raises(HTTPException) as exc_info:
            extractor.get_file_type("document.exe", "application/octet-stream")
        assert exc_info.value.status_code == 400
        assert "Unsupported file type" in exc_info.value.detail

    def test_case_insensitive_extension(self):
        """Should handle case-insensitive extensions"""
        extractor = get_file_extractor()
        file_type = extractor.get_file_type("DOCUMENT.PDF", "application/pdf")
        assert file_type.value == "pdf"

    def test_no_extension(self):
        """Should reject files without extension"""
        extractor = get_file_extractor()
        with pytest.raises(HTTPException) as exc_info:
            extractor.get_file_type("document", None)
        assert exc_info.value.status_code == 400


class TestTextExtraction:
    """Tests for text extraction from different file types"""

    def test_extract_from_txt_utf8(self):
        """Should extract text from UTF-8 text file"""
        extractor = get_file_extractor()
        content = b"This is a test document with UTF-8 encoding."
        result = extractor.extract_from_text(content)
        assert "test document" in result

    def test_extract_from_txt_latin1(self):
        """Should extract text from Latin-1 encoded file"""
        extractor = get_file_extractor()
        content = "This is a test document with special chars: café".encode("latin-1")
        result = extractor.extract_from_text(content)
        assert "test document" in result

    def test_extract_from_txt_invalid_encoding(self):
        """Should fail gracefully with invalid encoding"""
        extractor = get_file_extractor()
        # Create bytes that aren't valid in any common encoding
        content = bytes([0x80, 0x81, 0x82, 0x83, 0x84])
        # This should still work as latin-1 can decode any byte sequence
        result = extractor.extract_from_text(content)
        assert isinstance(result, str)


class TestFileSizeValidation:
    """Tests for file size validation"""

    @pytest.mark.asyncio
    async def test_empty_file_rejected(self):
        """Should reject empty files"""
        extractor = get_file_extractor()

        file = UploadFile(
            filename="empty.txt",
            file=io.BytesIO(b""),
        )

        with pytest.raises(HTTPException) as exc_info:
            await extractor.validate_file_size(file)
        assert exc_info.value.status_code == 400
        assert "empty" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_valid_file_size(self):
        """Should accept files within size limit"""
        extractor = get_file_extractor()

        content = b"This is valid content for testing."
        file = UploadFile(
            filename="valid.txt",
            file=io.BytesIO(content),
        )

        result = await extractor.validate_file_size(file)
        assert result == content


class TestSecurityMeasures:
    """Security-focused tests for file upload"""

    def test_path_traversal_prevention_unix(self):
        """Should strip path traversal attempts (Unix style)"""
        extractor = get_file_extractor()
        result = extractor.sanitize_filename("../../../etc/passwd.txt")
        assert result == "passwd.txt"
        assert "/" not in result
        assert ".." not in result

    def test_path_traversal_prevention_windows(self):
        """Should strip path traversal attempts (Windows style)"""
        extractor = get_file_extractor()
        result = extractor.sanitize_filename(
            "..\\..\\..\\Windows\\System32\\config.txt"
        )
        assert result == "config.txt"
        assert "\\" not in result
        assert ".." not in result

    def test_null_byte_removal(self):
        """Should remove null bytes from filename"""
        extractor = get_file_extractor()
        result = extractor.sanitize_filename("test\x00.txt")
        assert "\x00" not in result
        assert result == "test.txt"

    def test_magic_bytes_validation_pdf(self):
        """Should reject files with wrong magic bytes for PDF"""
        extractor = get_file_extractor()

        # A file claiming to be PDF but with wrong magic bytes
        fake_pdf_content = b"This is not a real PDF file content"

        with pytest.raises(HTTPException) as exc_info:
            extractor.validate_magic_bytes(fake_pdf_content, FileType.PDF)
        assert exc_info.value.status_code == 400
        assert "does not match" in exc_info.value.detail

    def test_magic_bytes_validation_pdf_valid(self):
        """Should accept files with correct PDF magic bytes"""
        extractor = get_file_extractor()

        # Real PDF magic bytes
        valid_pdf_start = b"%PDF-1.4\n..."

        # Should not raise
        extractor.validate_magic_bytes(valid_pdf_start, FileType.PDF)

    def test_magic_bytes_validation_docx(self):
        """Should reject files with wrong magic bytes for DOCX"""
        extractor = get_file_extractor()

        fake_docx_content = b"This is not a real DOCX file"

        with pytest.raises(HTTPException) as exc_info:
            extractor.validate_magic_bytes(fake_docx_content, FileType.DOCX)
        assert exc_info.value.status_code == 400

    def test_binary_file_rejected_as_txt(self):
        """Should reject binary files uploaded as .txt"""
        extractor = get_file_extractor()

        # Binary content (lots of non-printable characters)
        binary_content = bytes(range(256)) * 10

        with pytest.raises(HTTPException) as exc_info:
            extractor.validate_magic_bytes(binary_content, FileType.TXT)
        assert exc_info.value.status_code == 400
        assert "binary" in exc_info.value.detail.lower()

    def test_filename_length_limit(self):
        """Should truncate overly long filenames"""
        extractor = get_file_extractor()
        long_name = "a" * 500 + ".txt"
        result = extractor.sanitize_filename(long_name)
        assert len(result) <= 255
        assert result.endswith(".txt")

    def test_leading_dots_stripped(self):
        """Should strip leading dots (hidden files)"""
        extractor = get_file_extractor()
        result = extractor.sanitize_filename("...hidden.txt")
        assert not result.startswith(".")
        assert result == "hidden.txt"


class TestFullExtractionFlow:
    """Integration tests for the full extraction flow"""

    @pytest.mark.asyncio
    async def test_extract_text_from_txt_file(self):
        """Should extract and sanitize text from txt file"""
        extractor = get_file_extractor()

        content = b"""
        This is a test document.
        It has multiple paragraphs with political content.
        The government should support healthcare for all citizens.
        """

        file = UploadFile(
            filename="article.txt",
            file=io.BytesIO(content),
        )

        text, file_type, safe_filename = await extractor.extract_text(file)

        assert file_type.value == "txt"
        assert "political content" in text
        assert len(text) >= 10
        assert safe_filename == "article.txt"

    @pytest.mark.asyncio
    async def test_extract_text_too_short(self):
        """Should reject files with extracted text too short"""
        extractor = get_file_extractor()

        content = b"Short"  # Less than 10 characters

        file = UploadFile(
            filename="short.txt",
            file=io.BytesIO(content),
        )

        with pytest.raises(HTTPException) as exc_info:
            await extractor.extract_text(file)
        assert exc_info.value.status_code == 400
        assert "too short" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_missing_filename(self):
        """Should reject files without filename"""
        extractor = get_file_extractor()

        file = UploadFile(
            filename="",
            file=io.BytesIO(b"content"),
        )

        with pytest.raises(HTTPException) as exc_info:
            await extractor.extract_text(file)
        assert exc_info.value.status_code == 400
        assert "filename" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_path_traversal_in_filename(self):
        """Should sanitize path traversal attempts in filename"""
        extractor = get_file_extractor()

        content = b"This is a test document with enough content for validation."

        file = UploadFile(
            filename="../../../etc/passwd.txt",
            file=io.BytesIO(content),
        )

        text, file_type, safe_filename = await extractor.extract_text(file)

        # Filename should be sanitized - no path traversal
        assert safe_filename == "passwd.txt"
        assert "/" not in safe_filename
        assert ".." not in safe_filename


class TestGetFileExtractor:
    """Tests for the singleton pattern"""

    def test_returns_same_instance(self):
        """Should return the same cached instance"""
        instance1 = get_file_extractor()
        instance2 = get_file_extractor()
        assert instance1 is instance2

    def test_instance_is_file_extractor(self):
        """Should return a FileExtractor instance"""
        instance = get_file_extractor()
        assert isinstance(instance, FileExtractor)
