
import pytest
import pymupdf

from resume_engine.file_validator import (
    validate_pdf_file,
    validate_file_id,
    MAX_FILE_SIZE,
)

def create_valid_pdf():
    document = pymupdf.open()
    document.new_page()
    pdf_bytes = document.tobytes()
    document.close()
    return pdf_bytes


def test_valid_pdf():
    pdf_bytes = create_valid_pdf()

    result = validate_pdf_file(
        filename="resume.pdf",
        content_type="application/pdf",
        file_bytes=pdf_bytes,
    )

    assert result == 1


def test_invalid_extension():
    with pytest.raises(ValueError):
        validate_pdf_file(
            filename="resume.docx",
            content_type="application/pdf",
            file_bytes=create_valid_pdf(),
        )


def test_invalid_pdf_signature():
    with pytest.raises(ValueError):
        validate_pdf_file(
            filename="resume.pdf",
            content_type="application/pdf",
            file_bytes=b"This is not a PDF",
        )


def test_empty_pdf():
    with pytest.raises(ValueError):
        validate_pdf_file(
            filename="resume.pdf",
            content_type="application/pdf",
            file_bytes=b"",
        )


def test_invalid_content_type():
    with pytest.raises(ValueError):
        validate_pdf_file(
            filename="resume.pdf",
            content_type="text/plain",
            file_bytes=create_valid_pdf(),
        )

def test_password_protected_pdf():
    document = pymupdf.open()
    document.new_page()

    pdf_bytes = document.tobytes(
        encryption=pymupdf.PDF_ENCRYPT_AES_256,
        owner_pw="owner123",
        user_pw="user123",
    )
    document.close()

    with pytest.raises(ValueError, match="Password-protected"):
        validate_pdf_file(
            filename="protected.pdf",
            content_type="application/pdf",
            file_bytes=pdf_bytes,
        )


def test_pdf_exceeding_page_limit():
    document = pymupdf.open()

    for _ in range(101):
        document.new_page()

    pdf_bytes = document.tobytes()
    document.close()

    with pytest.raises(ValueError, match="100 pages"):
        validate_pdf_file(
            filename="large_pages.pdf",
            content_type="application/pdf",
            file_bytes=pdf_bytes,
        )


def test_corrupted_pdf_structure():
    corrupted_pdf = (
        b"%PDF-1.7\n"
        b"This is not a valid PDF structure\n"
        b"%%EOF"
    )

    with pytest.raises(ValueError, match="corrupted"):
        validate_pdf_file(
            filename="corrupted.pdf",
            content_type="application/pdf",
            file_bytes=corrupted_pdf,
        )


def test_pdf_exactly_at_maximum_size():
    pdf_bytes = create_valid_pdf()

    # Pad the valid PDF to exactly 5 MB.
    pdf_bytes += b"\n" * (MAX_FILE_SIZE - len(pdf_bytes))

    assert len(pdf_bytes) == MAX_FILE_SIZE

    result = validate_pdf_file(
        filename="exact_limit.pdf",
        content_type="application/pdf",
        file_bytes=pdf_bytes,
    )

    assert result == 1


# --- validate_file_id Tests ---

def test_validate_file_id_valid_lowercase():
    valid_id = "2ff5dbac5b1e47e8ab7452c92e3839f3"
    result = validate_file_id(valid_id)
    assert result == valid_id


def test_validate_file_id_valid_uppercase_normalized():
    upper_id = "2FF5DBAC5B1E47E8AB7452C92E3839F3"
    result = validate_file_id(upper_id)
    assert result == upper_id.lower()


def test_validate_file_id_with_whitespace():
    raw_id = "  2ff5dbac5b1e47e8ab7452c92e3839f3  "
    result = validate_file_id(raw_id)
    assert result == "2ff5dbac5b1e47e8ab7452c92e3839f3"


def test_validate_file_id_invalid_length():
    with pytest.raises(ValueError, match="32-character"):
        validate_file_id("2ff5dbac")

    with pytest.raises(ValueError, match="32-character"):
        validate_file_id("2ff5dbac5b1e47e8ab7452c92e3839f30000")


def test_validate_file_id_non_hex_characters():
    with pytest.raises(ValueError, match="32-character"):
        validate_file_id("2ff5dbac5b1e47e8ab7452c92e3839zz")


def test_validate_file_id_with_hyphens():
    with pytest.raises(ValueError, match="32-character"):
        validate_file_id("2ff5dbac-5b1e-47e8-ab74-52c92e3839f3")


def test_validate_file_id_empty_or_none():
    with pytest.raises(ValueError, match="missing or invalid"):
        validate_file_id("")

    with pytest.raises(ValueError, match="missing or invalid"):
        validate_file_id(None)


def test_validate_file_id_path_traversal():
    with pytest.raises(ValueError, match="32-character"):
        validate_file_id("../../../../etc/passwd")

    with pytest.raises(ValueError, match="32-character"):
        validate_file_id("..\\..\\uploads\\malicious.pdf")

