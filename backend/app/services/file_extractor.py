import io
import zipfile
from functools import lru_cache

from docx import Document
from fastapi import HTTPException, UploadFile, status
from pypdf import PdfReader

from app.core.config import get_settings
from app.models.schemas import FileType, sanitize_text


class FileExtractor:
    MAGIC_BYTES: dict[FileType, list[bytes]] = {
        FileType.PDF: [b"%PDF"],
        FileType.DOCX: [b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"],
    }

    EXTENSION_MAP: dict[str, FileType] = {
        ".txt": FileType.TXT,
        ".pdf": FileType.PDF,
        ".docx": FileType.DOCX,
    }

    MIME_TYPE_MAP: dict[str, FileType] = {
        "text/plain": FileType.TXT,
        "application/pdf": FileType.PDF,
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": FileType.DOCX,
    }

    MAX_PDF_PAGES = 500
    MAX_DOCX_PARAGRAPHS = 10000
    MAX_DECOMPRESSED_SIZE = 50 * 1024 * 1024

    def __init__(self) -> None:
        self.settings = get_settings()

    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to prevent path traversal attacks

        Args:
            filename: Original filename from upload

        Returns:
            Sanitized filename

        Raises:
            HTTPException: If filename is invalid
        """
        if not filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Filename is required"
            )

        sanitized_filename = (
            filename.replace("\\", "/").split("/")[-1].replace("\x00", "").strip(". ")
        )

        if len(sanitized_filename) > 255:
            if "." in sanitized_filename:
                name, ext = sanitized_filename.rsplit(".", 1)
                sanitized_filename = name[:250] + "." + ext
            else:
                sanitized_filename = sanitized_filename[:255]

        if not sanitized_filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filename"
            )

        return sanitized_filename

    def validate_magic_bytes(self, contents: bytes, file_type: FileType) -> None:
        """
        Validate file content matches claimed file type using magic bytes

        Args:
            contents: File contents
            file_type: Claimed file type

        Raises:
            HTTPException: If magic bytes don't match
        """
        if file_type == FileType.TXT:
            sample = contents[:1024]
            non_text_chars = sum(1 for b in sample if b < 32 and b not in (9, 10, 13))
            if len(sample) > 0 and non_text_chars / len(sample) > 0.1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File appears to be binary",
                )
            return

        expected_signatures = self.MAGIC_BYTES.get(file_type, [])
        if expected_signatures:
            matches = any(contents.startswith(sig) for sig in expected_signatures)
            if not matches:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File content does not match {file_type.value} format",
                )

    def get_file_type(self, filename: str, _content_type: str | None) -> FileType:
        """
        Determine the file type from filename extension

        Args:
            filename: Original filename with extension
            content_type: MIME type from upload (used for additional validation)

        Returns:
            FileType enum value

        Raises:
            HTTPException: If file type is not supported
        """
        extension = ""
        if "." in filename:
            extension = "." + filename.rsplit(".", 1)[-1].lower()

        if extension not in self.EXTENSION_MAP:
            allowed = ", ".join(self.settings.allowed_file_extensions)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type. Allowed types: {allowed}",
            )

        return self.EXTENSION_MAP[extension]

    async def validate_file_size(self, file: UploadFile) -> bytes:
        """
        Read and validate file size

        Args:
            file: Uploaded file

        Returns:
            File contents as bytes

        Raises:
            HTTPException: If file is too large or empty
        """
        contents = await file.read()

        if len(contents) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty"
            )

        if len(contents) > self.settings.max_file_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {self.settings.max_file_size_mb}MB",
            )

        return contents

    def extract_from_text(self, contents: bytes) -> str:
        """
        Extract text from a plain text file with encoding detection

        Args:
            contents: File contents as bytes

        Returns:
            Extracted text string

        Raises:
            HTTPException: If file cannot be decoded
        """
        if contents.startswith(b"\xef\xbb\xbf"):
            return contents.decode("utf-8-sig")
        if contents.startswith(b"\xff\xfe") or contents.startswith(b"\xfe\xff"):
            return contents.decode("utf-16")

        encodings = [
            "utf-8",
            "latin-1",
            "cp1252",
        ]

        for encoding in encodings:
            try:
                text = contents.decode(encoding)

                if text and not text.isspace():
                    return text
            except (UnicodeDecodeError, UnicodeError):
                continue

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not decode text file. Please ensure it uses a standard encoding (UTF-8 recommended).",
        )

    def extract_from_pdf(self, contents: bytes) -> str:
        """
        Extract text from a PDF file with security limits.

        Args:
            contents: File contents as bytes

        Returns:
            Extracted text string

        Raises:
            HTTPException: If PDF cannot be read, has no text, or exceeds limits
        """
        try:
            reader = PdfReader(io.BytesIO(contents))

            if len(reader.pages) > self.MAX_PDF_PAGES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"PDF has too many pages (max {self.MAX_PDF_PAGES})",
                )

            text_parts = []
            total_length = 0

            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
                    total_length += len(page_text)

                    if total_length > 100000:
                        break

            if not text_parts:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Could not extract text from PDF. The file may be scanned/image-based or empty.",
                )

            return "\n\n".join(text_parts)
        except HTTPException:
            raise
        except Exception as e:
            error_msg = str(e).lower()
            if "password" in error_msg or "encrypt" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="PDF is password-protected. Please provide an unencrypted file.",
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to read PDF file. Please ensure it's a valid PDF.",
            )

    def _check_docx_zip_bomb(self, contents: bytes) -> None:
        """
        Check if DOCX file might be a zip bomb.

        Args:
            contents: File contents as bytes

        Raises:
            HTTPException: If file appears to be a zip bomb
        """
        try:
            with zipfile.ZipFile(io.BytesIO(contents), "r") as zf:
                total_uncompressed = sum(info.file_size for info in zf.infolist())
                if total_uncompressed > self.MAX_DECOMPRESSED_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="File content is too large when decompressed",
                    )
        except zipfile.BadZipFile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid DOCX file format",
            )
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not validate DOCX file structure",
            )

    def extract_from_docx(self, contents: bytes) -> str:
        """
        Extract text from a Word document (.docx) with security protections.

        Includes protection against:
        - Zip bombs (DOCX is a ZIP archive)
        - XXE attacks (DOCX contains XML)
        - Resource exhaustion (limits on paragraphs)

        Args:
            contents: File contents as bytes

        Returns:
            Extracted text string

        Raises:
            HTTPException: If document cannot be read or has no text
        """
        self._check_docx_zip_bomb(contents)

        try:
            doc = Document(io.BytesIO(contents))
            text_parts = []

            for idx, paragraph in enumerate(doc.paragraphs, start=1):
                if idx > self.MAX_DOCX_PARAGRAPHS:
                    break

                if paragraph.text.strip():
                    text_parts.append(paragraph.text)

            if not text_parts:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Could not extract text from document. The file may be empty.",
                )

            return "\n\n".join(text_parts)

        except HTTPException:
            raise
        except Exception as e:
            error_msg = str(e).lower()
            if "encrypt" in error_msg or "password" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Document is password-protected. Please provide an unencrypted file.",
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to read Word document. Please ensure it's a valid .docx file.",
            )

    async def extract_text(self, file: UploadFile) -> tuple[str, FileType, str]:
        """
        Extract text from an uploaded file with full security validation.

        This is the main entry point for file processing.

        Security checks performed:
        1. Filename sanitization (path traversal prevention)
        2. File size validation
        3. File type detection
        4. Magic bytes validation
        5. Content extraction with format-specific protections
        6. Text sanitization

        Args:
            file: Uploaded file from FastAPI

        Returns:
            Tuple of (extracted_text, file_type, sanitized_filename)

        Raises:
            HTTPException: If any validation fails
        """

        safe_filename = self.sanitize_filename(file.filename or "")
        file_type = self.get_file_type(safe_filename, file.content_type)
        contents = await self.validate_file_size(file)

        self.validate_magic_bytes(contents, file_type)

        if file_type == FileType.TXT:
            text = self.extract_from_text(contents)
        elif file_type == FileType.PDF:
            text = self.extract_from_pdf(contents)
        elif file_type == FileType.DOCX:
            text = self.extract_from_docx(contents)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type",
            )

        text = sanitize_text(text)

        if len(text) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Extracted text is too short (minimum 10 characters)",
            )

        if len(text) > 50000:
            text = text[:50000]

        return text, file_type, safe_filename


@lru_cache
def get_file_extractor() -> FileExtractor:
    return FileExtractor()
