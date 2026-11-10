"""
CareerMind AI — Phase 1.1 Hardening Test Suite:
Migration Compatibility & File Cleanup Hardening.

Covers:
1. SQLite partial unique index permits multiple non-default resumes.
2. SQLite partial unique index prevents two default resumes.
3. PostgreSQL index definition contains the correct partial predicate.
4. Alembic upgrade and downgrade behavior.
5. Old PDF deletion PermissionError after successful commit.
6. Old PDF deletion OSError after successful commit.
7. New resume remains accessible after old PDF cleanup failure.
8. Database commit failure still preserves the original resume.
"""

import os
from pathlib import Path
from unittest.mock import patch
import pymupdf
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, text
from sqlalchemy.dialects import postgresql, sqlite
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.schema import CreateIndex
from alembic.config import Config
from alembic import command

from main import app
from database.base import Base
from database.session import get_db
from database.models.career_profile import CareerProfile
from database.models.resume_record import ResumeRecord
from services import storage_service, resume_library_service, career_profile_service
from api.v1.endpoints import resume as resume_endpoint
from api.v1.endpoints import jobs as jobs_endpoint

# Isolated test database in memory
TEST_DB_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def setup_isolated_env(tmp_path, monkeypatch):
    """Ensure clean in-memory database and isolated upload directory for each test."""
    Base.metadata.create_all(bind=test_engine)
    monkeypatch.setattr(resume_endpoint, "UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(storage_service, "UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(jobs_endpoint, "UPLOAD_DIR", tmp_path)

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


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


def create_sample_pdf(name="Jane Doe", email="jane@example.com") -> bytes:
    doc = pymupdf.open()
    page = doc.new_page()
    text_content = (
        f"{name}\n"
        f"{email} | +1 555-019-9988\n\n"
        f"Professional Summary\n"
        f"Backend developer.\n\n"
        f"Technical Skills\n"
        f"Programming: Python, SQL\n\n"
        f"Work Experience\n"
        f"Software Engineer — Tech Co.\n"
        f"2022 – Present\n"
        f"• Built REST APIs.\n"
    )
    page.insert_text((50, 72), text_content, fontsize=10)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


# -----------------------------------------------------------------------------
# 1. SQLite partial unique index permits multiple non-default resumes
# -----------------------------------------------------------------------------
def test_sqlite_partial_unique_index_permits_multiple_non_default_resumes(db_session):
    profile = career_profile_service.get_or_create_local_career_profile(db_session)

    # Insert 3 non-default resumes for the same profile
    rec1 = ResumeRecord(
        career_profile_id=profile.id,
        file_id="a" * 32,
        display_name="Resume A",
        original_filename="a.pdf",
        file_path="/data/a.pdf",
        file_size=1000,
        is_default=False,
    )
    rec2 = ResumeRecord(
        career_profile_id=profile.id,
        file_id="b" * 32,
        display_name="Resume B",
        original_filename="b.pdf",
        file_path="/data/b.pdf",
        file_size=1000,
        is_default=False,
    )
    rec3 = ResumeRecord(
        career_profile_id=profile.id,
        file_id="c" * 32,
        display_name="Resume C",
        original_filename="c.pdf",
        file_path="/data/c.pdf",
        file_size=1000,
        is_default=False,
    )

    db_session.add_all([rec1, rec2, rec3])
    db_session.commit()

    stmt = select(ResumeRecord).where(ResumeRecord.career_profile_id == profile.id)
    records = db_session.execute(stmt).scalars().all()
    assert len(records) == 3


# -----------------------------------------------------------------------------
# 2. SQLite partial unique index prevents two default resumes
# -----------------------------------------------------------------------------
def test_sqlite_partial_unique_index_prevents_two_default_resumes(db_session):
    profile = career_profile_service.get_or_create_local_career_profile(db_session)

    # First default resume
    rec1 = ResumeRecord(
        career_profile_id=profile.id,
        file_id="d" * 32,
        display_name="Default 1",
        original_filename="d1.pdf",
        file_path="/data/d1.pdf",
        file_size=1000,
        is_default=True,
    )
    db_session.add(rec1)
    db_session.commit()

    # Second default resume for the same career profile must raise IntegrityError
    rec2 = ResumeRecord(
        career_profile_id=profile.id,
        file_id="e" * 32,
        display_name="Default 2",
        original_filename="d2.pdf",
        file_path="/data/d2.pdf",
        file_size=1000,
        is_default=True,
    )
    db_session.add(rec2)
    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


# -----------------------------------------------------------------------------
# 3. PostgreSQL index definition contains the correct partial predicate
# -----------------------------------------------------------------------------
def test_postgresql_index_definition_contains_correct_partial_predicate():
    indexes = [idx for idx in ResumeRecord.__table__.indexes if idx.name == "uq_profile_default_resume"]
    assert len(indexes) == 1
    idx = indexes[0]

    # Verify PostgreSQL DDL compilation
    pg_ddl = str(CreateIndex(idx).compile(dialect=postgresql.dialect()))
    assert "WHERE is_default IS TRUE" in pg_ddl
    assert "CREATE UNIQUE INDEX uq_profile_default_resume" in pg_ddl

    # Verify SQLite DDL compilation
    sqlite_ddl = str(CreateIndex(idx).compile(dialect=sqlite.dialect()))
    assert "WHERE is_default = 1" in sqlite_ddl
    assert "CREATE UNIQUE INDEX uq_profile_default_resume" in sqlite_ddl


# -----------------------------------------------------------------------------
# 4. Alembic upgrade and downgrade behavior
# -----------------------------------------------------------------------------
def test_alembic_upgrade_and_downgrade_behavior(tmp_path, monkeypatch):
    temp_db_path = tmp_path / "migration_test.db"
    temp_url = f"sqlite:///{temp_db_path.as_posix()}"
    monkeypatch.setenv("DATABASE_URL", temp_url)

    alembic_cfg_path = Path(__file__).resolve().parents[2] / "alembic.ini"
    cfg = Config(str(alembic_cfg_path))
    cfg.set_main_option("sqlalchemy.url", temp_url)

    # 1. Upgrade to initial revision a15558c0f59e
    command.upgrade(cfg, "a15558c0f59e")

    # Verify initial revision reached
    conn = create_engine(temp_url).connect()
    version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
    assert version == "a15558c0f59e"

    # 2. Upgrade to new revision 633bb4235e1e
    command.upgrade(cfg, "633bb4235e1e")
    version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
    assert version == "633bb4235e1e"

    # Verify partial unique index exists after upgrade
    idx_sql = conn.execute(
        text("SELECT sql FROM sqlite_master WHERE name='uq_profile_default_resume'")
    ).scalar()
    assert idx_sql is not None
    assert "is_default = 1" in idx_sql

    # 3. Downgrade back to a15558c0f59e
    command.downgrade(cfg, "a15558c0f59e")
    version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
    assert version == "a15558c0f59e"

    # 4. Re-upgrade back to 633bb4235e1e
    command.upgrade(cfg, "633bb4235e1e")
    version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
    assert version == "633bb4235e1e"
    conn.close()


# -----------------------------------------------------------------------------
# 5. Old PDF deletion PermissionError after successful commit
# -----------------------------------------------------------------------------
def test_old_pdf_deletion_permission_error_after_successful_commit(client, tmp_path, caplog):
    pdf_old = create_sample_pdf(name="Alice Old", email="alice.old@example.com")
    pdf_new = create_sample_pdf(name="Alice New", email="alice.new@example.com")

    up = client.post("/api/v1/resumes/upload", files={"file": ("old.pdf", pdf_old, "application/pdf")})
    old_file_id = up.json()["file_id"]
    client.post(f"/api/v1/resumes/{old_file_id}/parse")

    real_delete_file = storage_service.delete_file

    def mock_delete_file(file_id, base_dir=None):
        if file_id == old_file_id:
            raise PermissionError(f"[WinError 32] The process cannot access the file: {file_id}.pdf")
        return real_delete_file(file_id, base_dir=base_dir)

    with patch("services.resume_library_service.delete_file", side_effect=mock_delete_file):
        rep_res = client.post(
            f"/api/v1/resumes/library/{old_file_id}/replace",
            files={"file": ("new.pdf", pdf_new, "application/pdf")},
        )

    # Replacement reports success (HTTP 200) because database and new file are committed
    assert rep_res.status_code == 200
    new_file_id = rep_res.json()["file_id"]

    # New file exists and is active
    assert (tmp_path / f"{new_file_id}.pdf").exists()
    # Old file still exists due to permission lock
    assert (tmp_path / f"{old_file_id}.pdf").exists()


# -----------------------------------------------------------------------------
# 6. Old PDF deletion OSError after successful commit
# -----------------------------------------------------------------------------
def test_old_pdf_deletion_os_error_after_successful_commit(client, tmp_path):
    pdf_old = create_sample_pdf(name="Bob Old")
    pdf_new = create_sample_pdf(name="Bob New")

    up = client.post("/api/v1/resumes/upload", files={"file": ("old.pdf", pdf_old, "application/pdf")})
    old_file_id = up.json()["file_id"]
    client.post(f"/api/v1/resumes/{old_file_id}/parse")

    real_delete_file = storage_service.delete_file

    def mock_delete_file(file_id, base_dir=None):
        if file_id == old_file_id:
            raise OSError(f"Disk I/O error unlinking {file_id}.pdf")
        return real_delete_file(file_id, base_dir=base_dir)

    with patch("services.resume_library_service.delete_file", side_effect=mock_delete_file):
        rep_res = client.post(
            f"/api/v1/resumes/library/{old_file_id}/replace",
            files={"file": ("new.pdf", pdf_new, "application/pdf")},
        )

    assert rep_res.status_code == 200
    new_file_id = rep_res.json()["file_id"]
    assert (tmp_path / f"{new_file_id}.pdf").exists()


# -----------------------------------------------------------------------------
# 7. New resume remains accessible after old PDF cleanup failure
# -----------------------------------------------------------------------------
def test_new_resume_remains_accessible_after_old_pdf_cleanup_failure(client, tmp_path):
    pdf_old = create_sample_pdf(name="Old Version", email="old.version@example.com")
    pdf_new = create_sample_pdf(name="New Version", email="new.version@example.com")

    up = client.post("/api/v1/resumes/upload", files={"file": ("old.pdf", pdf_old, "application/pdf")})
    old_file_id = up.json()["file_id"]
    client.post(f"/api/v1/resumes/{old_file_id}/parse")

    with patch("services.resume_library_service.delete_file", side_effect=PermissionError("Locked file")):
        rep_res = client.post(
            f"/api/v1/resumes/library/{old_file_id}/replace",
            files={"file": ("new.pdf", pdf_new, "application/pdf")},
        )
    assert rep_res.status_code == 200
    new_file_id = rep_res.json()["file_id"]

    # Retrieve new resume detail via library API
    detail_res = client.get(f"/api/v1/resumes/library/{new_file_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["file_id"] == new_file_id
    assert detail["candidate"]["personal_information"]["email"] == "new.version@example.com"


# -----------------------------------------------------------------------------
# 8. Database commit failure still preserves the original resume
# -----------------------------------------------------------------------------
def test_database_commit_failure_preserves_original_resume(client, db_session, tmp_path):
    pdf_old = create_sample_pdf(name="Original Candidate", email="original.safe@example.com")
    up = client.post("/api/v1/resumes/upload", files={"file": ("orig.pdf", pdf_old, "application/pdf")})
    orig_file_id = up.json()["file_id"]
    client.post(f"/api/v1/resumes/{orig_file_id}/parse")

    # Force database commit error
    with patch("services.resume_library_service.persist_parsed_candidate_profile", side_effect=Exception("DB failure")):
        pdf_new = create_sample_pdf(name="Should Fail")
        rep_res = client.post(
            f"/api/v1/resumes/library/{orig_file_id}/replace",
            files={"file": ("new.pdf", pdf_new, "application/pdf")},
        )
        assert rep_res.status_code == 500

    # Original file is preserved on disk
    assert (tmp_path / f"{orig_file_id}.pdf").exists()

    # No orphaned temporary files in uploads
    all_files = list(tmp_path.glob("*.pdf"))
    assert len(all_files) == 1
    assert all_files[0].name == f"{orig_file_id}.pdf"

    # Original DB record remains unchanged
    rec = db_session.execute(select(ResumeRecord).where(ResumeRecord.file_id == orig_file_id)).scalar_one()
    assert rec.file_id == orig_file_id

    # Original CandidateProfile details still load correctly
    detail = client.get(f"/api/v1/resumes/library/{orig_file_id}").json()
    assert detail["candidate"]["personal_information"]["email"] == "original.safe@example.com"
