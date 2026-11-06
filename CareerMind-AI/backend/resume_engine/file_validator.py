
from pathlib import Path
import pymupdf


MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_PDF_PAGES = 100

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/octet-stream",
}


def validate_pdf_file(
    filename: str,
    content_type: str | None,
    file_bytes: bytes,
) -> int:

    # Check filename
    if not filename:
        raise ValueError("Filename is missing.")

    # Check extension
    if Path(filename).suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are allowed.")

    # Check MIME type
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError("Invalid file content type.")

    # Check empty file
    if not file_bytes:
        raise ValueError("Uploaded file is empty.")

    # Check file size
    if len(file_bytes) > MAX_FILE_SIZE:
        raise ValueError("File size exceeds the 5 MB limit.")

    # Check PDF signature
    if b"%PDF-" not in file_bytes[:1024]:
        raise ValueError("Invalid PDF signature.")

    # Validate PDF structure
    try:
        document = pymupdf.open(
            stream=file_bytes,
            filetype="pdf"
        )

        try:
            if document.is_encrypted:
                raise ValueError(
                    "Password-protected PDFs are not supported."
                )

            page_count = document.page_count

            if page_count < 1:
                raise ValueError("PDF contains no pages.")

            if page_count > MAX_PDF_PAGES:
                raise ValueError(
                    "PDF cannot contain more than 100 pages."
                )

        finally:
            document.close()

    except ValueError:
        raise

    except Exception as exc:
        raise ValueError(
            "PDF is corrupted or cannot be opened."
        ) from exc

    return page_count
