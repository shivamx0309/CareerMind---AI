import uuid
import pymupdf
from fastapi.testclient import TestClient

from main import app
from api.v1.endpoints import resume as resume_endpoint


client = TestClient(app)


def create_pdf_with_text(text: str) -> bytes:
    """Create a single-page in-memory PDF containing the given text."""
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((50, 72), text)
    pdf_bytes = document.tobytes()
    document.close()
    return pdf_bytes


def create_multipage_pdf(page_texts: list[str]) -> bytes:
    """Create a multi-page in-memory PDF with text on each page."""
    document = pymupdf.open()
    for text in page_texts:
        page = document.new_page()
        page.insert_text((50, 72), text)
    pdf_bytes = document.tobytes()
    document.close()
    return pdf_bytes


def create_empty_text_pdf() -> bytes:
    """Create a valid PDF with one page but no text."""
    document = pymupdf.open()
    document.new_page()
    pdf_bytes = document.tobytes()
    document.close()
    return pdf_bytes


# 1. Valid uploaded PDF extracts text successfully
def test_extract_valid_pdf_success(monkeypatch, tmp_path):
    monkeypatch.setattr(resume_endpoint, "UPLOAD_DIR", tmp_path)

    file_id = uuid.uuid4().hex
    pdf_bytes = create_pdf_with_text(
        "SHIVAM KUMAR SINGH\nSoftware Engineer\nPython FastAPI PyTorch"
    )

    pdf_file = tmp_path / f"{file_id}.pdf"
    pdf_file.write_bytes(pdf_bytes)

    response = client.post(f"/api/v1/resumes/{file_id}/extract")

    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["file_id"] == file_id
    assert data["page_count"] == 1
    assert data["character_count"] > 0
    assert data["extraction_status"] == "completed"
    assert "SHIVAM KUMAR SINGH" in data["full_text"]
    assert "FastAPI" in data["full_text"]

    assert len(data["pages"]) == 1
    assert data["pages"][0]["page_number"] == 1
    assert "SHIVAM KUMAR SINGH" in data["pages"][0]["text"]
    assert data["pages"][0]["character_count"] == len(data["pages"][0]["text"])


# 2. Invalid file ID returns HTTP 400
def test_extract_invalid_file_id_returns_400(monkeypatch, tmp_path):
    monkeypatch.setattr(resume_endpoint, "UPLOAD_DIR", tmp_path)

    # Non-hex string
    response = client.post("/api/v1/resumes/invalid-id-xyz/extract")
    assert response.status_code == 400
    assert "Invalid file ID format" in response.json()["detail"]

    # Too short
    response = client.post("/api/v1/resumes/12345/extract")
    assert response.status_code == 400
    assert "Invalid file ID format" in response.json()["detail"]

    # Path traversal attempt / invalid characters
    response = client.post("/api/v1/resumes/invalid..id/extract")
    assert response.status_code == 400
    assert "Invalid file ID format" in response.json()["detail"]

    # Hyphenated UUID (not 32 hex)
    response = client.post("/api/v1/resumes/2ff5dbac-5b1e-47e8-ab74-52c92e3839f3/extract")
    assert response.status_code == 400


# 3. Valid UUID with missing PDF returns HTTP 404
def test_extract_missing_pdf_returns_404(monkeypatch, tmp_path):
    monkeypatch.setattr(resume_endpoint, "UPLOAD_DIR", tmp_path)

    missing_id = uuid.uuid4().hex
    response = client.post(f"/api/v1/resumes/{missing_id}/extract")

    assert response.status_code == 404
    assert "Resume file not found" in response.json()["detail"]


# 4. Empty-text PDF returns HTTP 422
def test_extract_empty_text_pdf_returns_422(monkeypatch, tmp_path):
    monkeypatch.setattr(resume_endpoint, "UPLOAD_DIR", tmp_path)

    file_id = uuid.uuid4().hex
    pdf_bytes = create_empty_text_pdf()

    pdf_file = tmp_path / f"{file_id}.pdf"
    pdf_file.write_bytes(pdf_bytes)

    response = client.post(f"/api/v1/resumes/{file_id}/extract")

    assert response.status_code == 422
    assert "No readable text found" in response.json()["detail"]


# 5. Corrupted stored PDF returns a controlled error (HTTP 422)
def test_extract_corrupted_pdf_returns_422(monkeypatch, tmp_path):
    monkeypatch.setattr(resume_endpoint, "UPLOAD_DIR", tmp_path)

    file_id = uuid.uuid4().hex
    corrupted_bytes = b"%PDF-1.7\nCorrupted binary content without xref\n%%EOF"

    pdf_file = tmp_path / f"{file_id}.pdf"
    pdf_file.write_bytes(corrupted_bytes)

    response = client.post(f"/api/v1/resumes/{file_id}/extract")

    assert response.status_code == 422
    assert "Unable to extract text" in response.json()["detail"]


# 6. Multi-page PDF returns correct page count and page-wise text
def test_extract_multipage_pdf_success(monkeypatch, tmp_path):
    monkeypatch.setattr(resume_endpoint, "UPLOAD_DIR", tmp_path)

    file_id = uuid.uuid4().hex
    page_texts = [
        "Page 1: Profile and Summary for Candidate",
        "Page 2: Work Experience and Projects at Tech Corp",
        "Page 3: Education and Technical Skills Certification",
    ]
    pdf_bytes = create_multipage_pdf(page_texts)

    pdf_file = tmp_path / f"{file_id}.pdf"
    pdf_file.write_bytes(pdf_bytes)

    response = client.post(f"/api/v1/resumes/{file_id}/extract")

    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["file_id"] == file_id
    assert data["page_count"] == 3
    assert data["character_count"] > 0
    assert len(data["pages"]) == 3

    for idx, expected_text in enumerate(page_texts, start=1):
        page_data = data["pages"][idx - 1]
        assert page_data["page_number"] == idx
        assert expected_text in page_data["text"]
        assert page_data["character_count"] == len(page_data["text"])
        assert expected_text in data["full_text"]


# 7. End-to-end: Upload endpoint -> Extract endpoint
def test_end_to_end_upload_and_extract(monkeypatch, tmp_path):
    monkeypatch.setattr(resume_endpoint, "UPLOAD_DIR", tmp_path)

    sample_text = "Alice Johnson\nFull Stack Developer\nReact, TypeScript, FastAPI"
    pdf_bytes = create_pdf_with_text(sample_text)

    # Step 1: Upload resume
    upload_response = client.post(
        "/api/v1/resumes/upload",
        files={
            "file": (
                "alice_resume.pdf",
                pdf_bytes,
                "application/pdf",
            )
        },
    )

    assert upload_response.status_code == 201
    upload_data = upload_response.json()
    assert upload_data["success"] is True
    file_id = upload_data["file_id"]

    # Step 2: Extract text using returned file_id
    extract_response = client.post(f"/api/v1/resumes/{file_id}/extract")

    assert extract_response.status_code == 200
    extract_data = extract_response.json()
    assert extract_data["success"] is True
    assert extract_data["file_id"] == file_id
    assert extract_data["page_count"] == 1
    assert "Alice Johnson" in extract_data["full_text"]
    assert "FastAPI" in extract_data["full_text"]
