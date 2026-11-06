
import pymupdf
from fastapi.testclient import TestClient

from main import app
from api.v1.endpoints import resume as resume_endpoint


client = TestClient(app)


def create_valid_pdf():
    document = pymupdf.open()
    document.new_page()
    pdf_bytes = document.tobytes()
    document.close()
    return pdf_bytes


def test_upload_valid_resume(monkeypatch, tmp_path):
    monkeypatch.setattr(resume_endpoint, "UPLOAD_DIR", tmp_path)

    response = client.post(
        "/api/v1/resumes/upload",
        files={
            "file": (
                "resume.pdf",
                create_valid_pdf(),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["success"] is True
    assert data["original_filename"] == "resume.pdf"
    assert data["page_count"] == 1
    assert data["extraction_status"] == "pending"

    saved_file = tmp_path / f'{data["file_id"]}.pdf'
    assert saved_file.exists()
    assert saved_file.stat().st_size > 0


def test_upload_invalid_extension(monkeypatch, tmp_path):
    monkeypatch.setattr(resume_endpoint, "UPLOAD_DIR", tmp_path)

    response = client.post(
        "/api/v1/resumes/upload",
        files={
            "file": (
                "resume.docx",
                create_valid_pdf(),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400
    assert "Only PDF files are allowed." in response.json()["detail"]


def test_upload_invalid_pdf(monkeypatch, tmp_path):
    monkeypatch.setattr(resume_endpoint, "UPLOAD_DIR", tmp_path)

    response = client.post(
        "/api/v1/resumes/upload",
        files={
            "file": (
                "resume.pdf",
                b"This is not a PDF",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400
    assert "Invalid PDF signature." in response.json()["detail"]


def test_upload_file_too_large(monkeypatch, tmp_path):
    monkeypatch.setattr(resume_endpoint, "UPLOAD_DIR", tmp_path)

    oversized_content = b"x" * (
        resume_endpoint.MAX_FILE_SIZE + 1
    )

    response = client.post(
        "/api/v1/resumes/upload",
        files={
            "file": (
                "large_resume.pdf",
                oversized_content,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 413
    assert "5 MB limit" in response.json()["detail"]
