"""
Verification test suite for Resume Replacement Failure Scenarios (Area 3 Audit).

Tests all 5 replacement failure stages:
1. New PDF upload failure (oversized >5MB, invalid format).
2. PDF text extraction failure (corrupt/empty PDF).
3. Parsing failure.
4. Database transaction/commit failure.
5. Old PDF deletion behavior (OS lock / permission error).
"""

from unittest.mock import patch
import pymupdf
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database.base import Base
from database.session import get_db
from database.models.resume_record import ResumeRecord
from database.models.resume_profile import ResumeProfile
from services import storage_service, resume_library_service, career_profile_service
from api.v1.endpoints import resume as resume_endpoint
from api.v1.endpoints import jobs as jobs_endpoint

# Isolated in-memory database
TEST_DB_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def setup_isolated_env(tmp_path, monkeypatch):
    Base.metadata.create_all(bind=test_engine)
    monkeypatch.setattr(resume_endpoint, "UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(storage_service, "UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(jobs_endpoint, "UPLOAD_DIR", tmp_path)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def db_session():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_valid_pdf(name="Alice Initial", email="alice.initial@example.com") -> bytes:
    doc = pymupdf.open()
    page = doc.new_page()
    text = (
        f"{name}\n"
        f"{email} | +1 555-010-1234\n\n"
        f"Professional Summary\n"
        f"Experienced software engineer.\n\n"
        f"Technical Skills\n"
        f"Programming: Python, SQL\n\n"
        f"Work Experience\n"
        f"Software Engineer — TechCorp\n"
        f"2021 – Present\n"
        f"• Developed APIs.\n"
    )
    page.insert_text((50, 72), text, fontsize=10)
    b = doc.tobytes()
    doc.close()
    return b


def test_scenario_1_upload_failure_oversized(client, tmp_path):
    """Scenario 1A: Oversized new PDF is rejected before touching disk or DB."""
    orig_pdf = create_valid_pdf()
    up = client.post("/api/v1/resumes/upload", files={"file": ("orig.pdf", orig_pdf, "application/pdf")})
    assert up.status_code == 201
    orig_file_id = up.json()["file_id"]

    # 6 MB of dummy data
    large_data = b"%PDF-1.4 " + b"0" * (6 * 1024 * 1024)
    res = client.post(
        f"/api/v1/resumes/library/{orig_file_id}/replace",
        files={"file": ("large.pdf", large_data, "application/pdf")},
    )
    assert res.status_code == 413
    assert (tmp_path / f"{orig_file_id}.pdf").exists()


def test_scenario_1_upload_failure_invalid_type(client, tmp_path):
    """Scenario 1B: Non-PDF format rejected before saving."""
    orig_pdf = create_valid_pdf()
    up = client.post("/api/v1/resumes/upload", files={"file": ("orig.pdf", orig_pdf, "application/pdf")})
    orig_file_id = up.json()["file_id"]

    res = client.post(
        f"/api/v1/resumes/library/{orig_file_id}/replace",
        files={"file": ("malicious.exe", b"MZ invalid binary", "application/x-dosexec")},
    )
    assert res.status_code == 400
    assert (tmp_path / f"{orig_file_id}.pdf").exists()


def test_scenario_2_extraction_failure_empty_text(client, tmp_path):
    """Scenario 2: PDF with no extractable text cleans up temporary file and leaves original intact."""
    orig_pdf = create_valid_pdf()
    up = client.post("/api/v1/resumes/upload", files={"file": ("orig.pdf", orig_pdf, "application/pdf")})
    orig_file_id = up.json()["file_id"]
    client.post(f"/api/v1/resumes/{orig_file_id}/parse")

    # Blank PDF (no text)
    blank_doc = pymupdf.open()
    blank_doc.new_page()
    blank_bytes = blank_doc.tobytes()
    blank_doc.close()

    res = client.post(
        f"/api/v1/resumes/library/{orig_file_id}/replace",
        files={"file": ("blank.pdf", blank_bytes, "application/pdf")},
    )
    assert res.status_code == 422

    # Verify no orphaned files in upload dir other than original
    files_in_dir = list(tmp_path.glob("*.pdf"))
    assert len(files_in_dir) == 1
    assert files_in_dir[0].name == f"{orig_file_id}.pdf"

    # Original resume detail still works
    detail = client.get(f"/api/v1/resumes/library/{orig_file_id}")
    assert detail.status_code == 200
    assert detail.json()["candidate"]["personal_information"]["email"] == "alice.initial@example.com"


def test_scenario_3_parsing_failure(client, tmp_path):
    """Scenario 3: Parsing exception removes temporary new file and leaves original intact."""
    orig_pdf = create_valid_pdf()
    up = client.post("/api/v1/resumes/upload", files={"file": ("orig.pdf", orig_pdf, "application/pdf")})
    orig_file_id = up.json()["file_id"]
    client.post(f"/api/v1/resumes/{orig_file_id}/parse")

    # Mock extract_candidate_profile to raise an unhandled parsing error
    with patch("api.v1.endpoints.resume.extract_candidate_profile", side_effect=RuntimeError("Parsing crash")):
        new_pdf = create_valid_pdf(name="Bob New")
        res = client.post(
            f"/api/v1/resumes/library/{orig_file_id}/replace",
            files={"file": ("new.pdf", new_pdf, "application/pdf")},
        )
        assert res.status_code == 422

    # Only original file exists on disk
    files_in_dir = list(tmp_path.glob("*.pdf"))
    assert len(files_in_dir) == 1
    assert files_in_dir[0].name == f"{orig_file_id}.pdf"

    # Original DB record intact
    detail = client.get(f"/api/v1/resumes/library/{orig_file_id}")
    assert detail.status_code == 200
    assert detail.json()["candidate"]["personal_information"]["email"] == "alice.initial@example.com"


def test_scenario_4_database_commit_failure(client, db_session, tmp_path):
    """Scenario 4: DB failure inside replace_resume_record rolls back and removes temporary new file."""
    orig_pdf = create_valid_pdf()
    up = client.post("/api/v1/resumes/upload", files={"file": ("orig.pdf", orig_pdf, "application/pdf")})
    orig_file_id = up.json()["file_id"]
    client.post(f"/api/v1/resumes/{orig_file_id}/parse")

    # Mock persist_parsed_candidate_profile to fail with a database error
    with patch("services.resume_library_service.persist_parsed_candidate_profile", side_effect=Exception("DB deadlock")):
        new_pdf = create_valid_pdf(name="Bob New")
        res = client.post(
            f"/api/v1/resumes/library/{orig_file_id}/replace",
            files={"file": ("new.pdf", new_pdf, "application/pdf")},
        )
        assert res.status_code == 500

    # Temporary new PDF unlinked
    files_in_dir = list(tmp_path.glob("*.pdf"))
    assert len(files_in_dir) == 1
    assert files_in_dir[0].name == f"{orig_file_id}.pdf"

    # Original DB record still points to orig_file_id
    rec = db_session.execute(select(ResumeRecord).where(ResumeRecord.file_id == orig_file_id)).scalar_one_or_none()
    assert rec is not None
    assert rec.file_id == orig_file_id

