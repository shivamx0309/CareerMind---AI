"""
CareerMind AI — Phase 1 Test Suite: Existing SQLite Database Integration & Resume Persistence.

Verifies all 17 required scenarios:
1. Resume upload creates a database record.
2. Parsing persists all CandidateProfile fields.
3. All 10 skill categories reconstruct correctly.
4. Achievements survive persistence and reconstruction.
5. Re-parsing does not duplicate child records (idempotent).
6. Multiple resumes remain independent.
7. Setting a default resume works.
8. Only one default resume exists.
9. Deleting a default reassigns another resume.
10. Deleting one resume does not affect another.
11. Replacement success.
12. Replacement failure preserves the original.
13. Invalid and corrupted PDF handling.
14. Missing PDF file handling.
15. Path traversal protection.
16. Job Matcher regression.
17. Existing onboarding regression.
"""

import uuid
from pathlib import Path
import pymupdf
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database.base import Base
from database.session import get_db
from database.models.career_profile import CareerProfile
from database.models.resume_record import ResumeRecord
from database.models.resume_profile import ResumeProfile
from database.models.resume_skill import ResumeSkill
from database.models.resume_education import ResumeEducation
from database.models.resume_experience import ResumeExperience
from database.models.resume_project import ResumeProject
from database.models.resume_certification import ResumeCertification
from schemas.candidate_schema import (
    CandidateProfile,
    PersonalInformation,
    TechnicalSkills,
    EducationEntry,
    ExperienceEntry,
    ProjectEntry,
    CertificationEntry,
    AchievementEntry,
)
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
def isolated_db_and_storage(tmp_path, monkeypatch):
    """Ensure every test runs on a clean in-memory database and temporary upload directory."""
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


def create_synthetic_pdf(
    name="Jane Doe",
    email="jane.doe@example.com",
    title="Senior Python Backend Engineer",
    skills="Python, SQL, FastAPI, Docker, PostgreSQL, Redis",
) -> bytes:
    """Generate a clean synthetic PDF with readable text."""
    doc = pymupdf.open()
    page = doc.new_page()
    text = (
        f"{name}\n"
        f"{email} | +1 555-010-9988 | San Francisco, CA\n"
        f"https://linkedin.com/in/janedoe | https://github.com/janedoe\n\n"
        f"Professional Summary\n"
        f"Passionate {title} specializing in distributed systems, RESTful microservices, and databases.\n\n"
        f"Technical Skills\n"
        f"Programming: {skills}\n"
        f"Frameworks: FastAPI, Django, Flask\n"
        f"Databases: PostgreSQL, MySQL, Redis\n\n"
        f"Work Experience\n"
        f"Senior Backend Engineer — TechCorp Inc.\n"
        f"Jan 2021 – Present\n"
        f"• Designed and maintained high-throughput API endpoints with FastAPI.\n"
        f"• Optimized database indexes, reducing query latency by 40%.\n\n"
        f"Education\n"
        f"Bachelor of Science in Computer Science\n"
        f"Stanford University | 2017 – 2021 | GPA 3.9/4.0\n\n"
        f"Projects\n"
        f"CloudPipeline\n"
        f"• Engineered automated continuous deployment pipeline using Docker and GitHub Actions.\n\n"
        f"Certifications\n"
        f"AWS Certified Solutions Architect — Amazon Web Services | 2022\n\n"
        f"Achievements\n"
        f"• Won 1st place in University Hackathon 2020\n"
    )
    page.insert_text((50, 72), text, fontsize=10)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


# -----------------------------------------------------------------------------
# 1. Resume upload creates a database record
# -----------------------------------------------------------------------------
def test_resume_upload_creates_database_record(client, db_session, tmp_path):
    pdf = create_synthetic_pdf()
    res = client.post(
        "/api/v1/resumes/upload",
        files={"file": ("my_resume.pdf", pdf, "application/pdf")},
    )
    assert res.status_code == 201
    data = res.json()
    file_id = data["file_id"]

    stmt = select(ResumeRecord).where(ResumeRecord.file_id == file_id)
    record = db_session.execute(stmt).scalar_one_or_none()
    assert record is not None
    assert record.original_filename == "my_resume.pdf"
    assert record.is_default is True
    assert record.upload_status == "completed"
    assert record.parsing_status == "pending"
    assert (tmp_path / f"{file_id}.pdf").exists()


# -----------------------------------------------------------------------------
# 2. Parsing persists all CandidateProfile fields
# -----------------------------------------------------------------------------
def test_parsing_persists_all_candidate_profile_fields(client, db_session):
    pdf = create_synthetic_pdf()
    up_res = client.post(
        "/api/v1/resumes/upload",
        files={"file": ("profile_resume.pdf", pdf, "application/pdf")},
    )
    file_id = up_res.json()["file_id"]

    parse_res = client.post(f"/api/v1/resumes/{file_id}/parse")
    assert parse_res.status_code == 200
    p_data = parse_res.json()
    assert p_data["success"] is True

    stmt = select(ResumeRecord).where(ResumeRecord.file_id == file_id)
    record = db_session.execute(stmt).scalar_one()
    assert record.parsing_status == "completed"
    assert record.last_parsed_at is not None

    rp = db_session.execute(select(ResumeProfile).where(ResumeProfile.resume_record_id == record.id)).scalar_one()
    assert rp.full_name is not None
    assert rp.email == "jane.doe@example.com"
    assert rp.professional_summary is not None

    # Verify child tables populated
    skills = db_session.execute(select(ResumeSkill).where(ResumeSkill.resume_profile_id == rp.id)).scalars().all()
    assert len(skills) > 0

    educations = db_session.execute(select(ResumeEducation).where(ResumeEducation.resume_profile_id == rp.id)).scalars().all()
    assert len(educations) > 0

    experiences = db_session.execute(select(ResumeExperience).where(ResumeExperience.resume_profile_id == rp.id)).scalars().all()
    assert len(experiences) > 0


# -----------------------------------------------------------------------------
# 3. All 10 skill categories reconstruct correctly
# -----------------------------------------------------------------------------
def test_all_10_skill_categories_reconstruct_correctly(db_session):
    profile = career_profile_service.get_or_create_local_career_profile(db_session)
    rec = resume_library_service.register_uploaded_resume(
        db_session,
        career_profile_id=profile.id,
        file_id="1" * 32,
        original_filename="skills.pdf",
        file_size=1024,
    )

    test_skills = TechnicalSkills(
        programming_languages=["Python", "Go"],
        frontend=["React", "Vue"],
        backend=["FastAPI", "Django"],
        databases=["PostgreSQL", "Redis"],
        data_analytics=["Pandas", "NumPy"],
        machine_learning=["Scikit-Learn"],
        deep_learning=["PyTorch", "TensorFlow"],
        cloud_devops=["Docker", "Kubernetes", "AWS"],
        tools=["Git", "VS Code"],
        other=["REST APIs", "Microservices"],
    )

    candidate = CandidateProfile(
        personal_information=PersonalInformation(full_name="Tester"),
        technical_skills=test_skills,
    )

    resume_library_service.persist_parsed_candidate_profile(db_session, rec.id, candidate)
    reconstituted = resume_library_service.reconstitute_candidate_profile(db_session, rec.id)

    assert reconstituted is not None
    ts = reconstituted.technical_skills
    for cat in resume_library_service.TECHNICAL_SKILL_CATEGORIES:
        expected = getattr(test_skills, cat)
        actual = getattr(ts, cat)
        assert set(actual) == set(expected), f"Category {cat} mismatch"


# -----------------------------------------------------------------------------
# 4. Achievements survive persistence and reconstruction
# -----------------------------------------------------------------------------
def test_achievements_survive_persistence_and_reconstruction(db_session):
    profile = career_profile_service.get_or_create_local_career_profile(db_session)
    rec = resume_library_service.register_uploaded_resume(
        db_session,
        career_profile_id=profile.id,
        file_id="2" * 32,
        original_filename="achievements.pdf",
        file_size=1024,
    )

    achievements = [
        AchievementEntry(
            title="National Hackathon Winner",
            description="Built an AI assistant",
            date="2024",
            organization="TechFest",
        ),
        AchievementEntry(
            title="Dean's List Award",
            description="Top 5% student",
            date="2023",
        ),
    ]

    candidate = CandidateProfile(
        personal_information=PersonalInformation(full_name="Achiever"),
        achievements=achievements,
    )

    resume_library_service.persist_parsed_candidate_profile(db_session, rec.id, candidate)
    reconstituted = resume_library_service.reconstitute_candidate_profile(db_session, rec.id)

    assert reconstituted is not None
    assert len(reconstituted.achievements) == 2
    assert reconstituted.achievements[0].title == "National Hackathon Winner"
    assert reconstituted.achievements[1].title == "Dean's List Award"


# -----------------------------------------------------------------------------
# 5. Re-parsing does not duplicate child records
# -----------------------------------------------------------------------------
def test_reparsing_idempotent_no_duplicate_child_records(client, db_session):
    pdf = create_synthetic_pdf()
    up = client.post("/api/v1/resumes/upload", files={"file": ("idempotent.pdf", pdf, "application/pdf")})
    file_id = up.json()["file_id"]

    # Parse 1st time
    res1 = client.post(f"/api/v1/resumes/{file_id}/parse")
    assert res1.status_code == 200

    rec = db_session.execute(select(ResumeRecord).where(ResumeRecord.file_id == file_id)).scalar_one()
    rp = db_session.execute(select(ResumeProfile).where(ResumeProfile.resume_record_id == rec.id)).scalar_one()
    skill_count_1 = len(db_session.execute(select(ResumeSkill).where(ResumeSkill.resume_profile_id == rp.id)).scalars().all())

    # Parse 2nd time
    res2 = client.post(f"/api/v1/resumes/{file_id}/parse")
    assert res2.status_code == 200

    rp2 = db_session.execute(select(ResumeProfile).where(ResumeProfile.resume_record_id == rec.id)).scalar_one()
    skill_count_2 = len(db_session.execute(select(ResumeSkill).where(ResumeSkill.resume_profile_id == rp2.id)).scalars().all())

    assert skill_count_1 == skill_count_2
    assert len(db_session.execute(select(ResumeProfile).where(ResumeProfile.resume_record_id == rec.id)).scalars().all()) == 1


# -----------------------------------------------------------------------------
# 6. Multiple resumes remain independent
# -----------------------------------------------------------------------------
def test_multiple_resumes_remain_independent(client, db_session):
    pdf1 = create_synthetic_pdf(name="Alice Engineer", email="alice@example.com")
    pdf2 = create_synthetic_pdf(name="Bob Designer", email="bob@example.com")

    up1 = client.post("/api/v1/resumes/upload", files={"file": ("alice.pdf", pdf1, "application/pdf")})
    up2 = client.post("/api/v1/resumes/upload", files={"file": ("bob.pdf", pdf2, "application/pdf")})

    f1 = up1.json()["file_id"]
    f2 = up2.json()["file_id"]

    client.post(f"/api/v1/resumes/{f1}/parse")
    client.post(f"/api/v1/resumes/{f2}/parse")

    detail1 = client.get(f"/api/v1/resumes/library/{f1}").json()
    detail2 = client.get(f"/api/v1/resumes/library/{f2}").json()

    assert detail1["candidate"]["personal_information"]["email"] == "alice@example.com"
    assert detail2["candidate"]["personal_information"]["email"] == "bob@example.com"


# -----------------------------------------------------------------------------
# 7. Setting a default resume works
# -----------------------------------------------------------------------------
def test_setting_default_resume_works(client, db_session):
    pdf1 = create_synthetic_pdf(name="Resume 1")
    pdf2 = create_synthetic_pdf(name="Resume 2")

    f1 = client.post("/api/v1/resumes/upload", files={"file": ("r1.pdf", pdf1, "application/pdf")}).json()["file_id"]
    f2 = client.post("/api/v1/resumes/upload", files={"file": ("r2.pdf", pdf2, "application/pdf")}).json()["file_id"]

    # First uploaded is default
    r1 = client.get(f"/api/v1/resumes/library/{f1}").json()
    r2 = client.get(f"/api/v1/resumes/library/{f2}").json()
    assert r1["is_default"] is True
    assert r2["is_default"] is False

    # Switch default to r2
    res = client.put(f"/api/v1/resumes/library/{f2}/default")
    assert res.status_code == 200
    assert res.json()["is_default"] is True

    r1_after = client.get(f"/api/v1/resumes/library/{f1}").json()
    r2_after = client.get(f"/api/v1/resumes/library/{f2}").json()
    assert r1_after["is_default"] is False
    assert r2_after["is_default"] is True


# -----------------------------------------------------------------------------
# 8. Only one default resume exists
# -----------------------------------------------------------------------------
def test_only_one_default_resume_exists(client, db_session):
    for i in range(3):
        pdf = create_synthetic_pdf(name=f"Candidate {i}")
        client.post("/api/v1/resumes/upload", files={"file": (f"c{i}.pdf", pdf, "application/pdf")})

    lib = client.get("/api/v1/resumes/library").json()
    defaults = [r for r in lib if r["is_default"]]
    assert len(defaults) == 1


# -----------------------------------------------------------------------------
# 9. Deleting a default reassigns another resume
# -----------------------------------------------------------------------------
def test_deleting_default_reassigns_another_resume(client, db_session):
    pdf1 = create_synthetic_pdf(name="First")
    pdf2 = create_synthetic_pdf(name="Second")

    f1 = client.post("/api/v1/resumes/upload", files={"file": ("first.pdf", pdf1, "application/pdf")}).json()["file_id"]
    f2 = client.post("/api/v1/resumes/upload", files={"file": ("second.pdf", pdf2, "application/pdf")}).json()["file_id"]

    # Delete default (f1)
    del_res = client.delete(f"/api/v1/resumes/library/{f1}")
    assert del_res.status_code == 200

    r2 = client.get(f"/api/v1/resumes/library/{f2}").json()
    assert r2["is_default"] is True


# -----------------------------------------------------------------------------
# 10. Deleting one resume does not affect another
# -----------------------------------------------------------------------------
def test_deleting_one_resume_does_not_affect_another(client, db_session, tmp_path):
    pdf1 = create_synthetic_pdf(name="Keep Me")
    pdf2 = create_synthetic_pdf(name="Delete Me")

    f1 = client.post("/api/v1/resumes/upload", files={"file": ("keep.pdf", pdf1, "application/pdf")}).json()["file_id"]
    f2 = client.post("/api/v1/resumes/upload", files={"file": ("delete.pdf", pdf2, "application/pdf")}).json()["file_id"]

    client.post(f"/api/v1/resumes/{f1}/parse")
    client.post(f"/api/v1/resumes/{f2}/parse")

    client.delete(f"/api/v1/resumes/library/{f2}")

    # f2 deleted from DB and disk
    assert client.get(f"/api/v1/resumes/library/{f2}").status_code == 404
    assert not (tmp_path / f"{f2}.pdf").exists()

    # f1 still exists in DB and disk
    r1 = client.get(f"/api/v1/resumes/library/{f1}")
    assert r1.status_code == 200
    assert (tmp_path / f"{f1}.pdf").exists()


# -----------------------------------------------------------------------------
# 11. Replacement success
# -----------------------------------------------------------------------------
def test_replacement_success(client, db_session, tmp_path):
    pdf_old = create_synthetic_pdf(name="Old Name", email="old@example.com")
    pdf_new = create_synthetic_pdf(name="New Name", email="new@example.com")

    f_old = client.post("/api/v1/resumes/upload", files={"file": ("old.pdf", pdf_old, "application/pdf")}).json()["file_id"]
    client.post(f"/api/v1/resumes/{f_old}/parse")

    rep_res = client.post(
        f"/api/v1/resumes/library/{f_old}/replace",
        files={"file": ("new.pdf", pdf_new, "application/pdf")},
        data={"display_name": "Updated Resume"},
    )
    assert rep_res.status_code == 200
    rep_data = rep_res.json()

    new_file_id = rep_data["file_id"]
    assert new_file_id != f_old
    assert rep_data["display_name"] == "Updated Resume"

    # Old file removed from disk
    assert not (tmp_path / f"{f_old}.pdf").exists()
    # New file exists on disk
    assert (tmp_path / f"{new_file_id}.pdf").exists()

    # Parsed profile is updated
    detail = client.get(f"/api/v1/resumes/library/{new_file_id}").json()
    assert detail["candidate"]["personal_information"]["email"] == "new@example.com"


# -----------------------------------------------------------------------------
# 12. Replacement failure preserves the original
# -----------------------------------------------------------------------------
def test_replacement_failure_preserves_original(client, db_session, tmp_path):
    pdf_old = create_synthetic_pdf(name="Original", email="original@example.com")
    f_old = client.post("/api/v1/resumes/upload", files={"file": ("orig.pdf", pdf_old, "application/pdf")}).json()["file_id"]
    client.post(f"/api/v1/resumes/{f_old}/parse")

    # Replace with corrupt file
    corrupt_bytes = b"%PDF-1.4 corrupt content that cannot be parsed as valid PDF text"
    rep_res = client.post(
        f"/api/v1/resumes/library/{f_old}/replace",
        files={"file": ("corrupt.pdf", corrupt_bytes, "application/pdf")},
    )
    assert rep_res.status_code in [400, 422]

    # Original record and file remain intact
    detail = client.get(f"/api/v1/resumes/library/{f_old}")
    assert detail.status_code == 200
    assert detail.json()["candidate"]["personal_information"]["email"] == "original@example.com"
    assert (tmp_path / f"{f_old}.pdf").exists()


# -----------------------------------------------------------------------------
# 13. Invalid and corrupted PDF handling
# -----------------------------------------------------------------------------
def test_invalid_and_corrupted_pdf_handling(client):
    res_text = client.post(
        "/api/v1/resumes/upload",
        files={"file": ("doc.txt", b"plain text is not a PDF", "text/plain")},
    )
    assert res_text.status_code == 400

    res_fake_pdf = client.post(
        "/api/v1/resumes/upload",
        files={"file": ("fake.pdf", b"not a real pdf header", "application/pdf")},
    )
    assert res_fake_pdf.status_code == 400


# -----------------------------------------------------------------------------
# 14. Missing PDF file handling
# -----------------------------------------------------------------------------
def test_missing_pdf_file_handling(client):
    missing_id = "0" * 32
    res_parse = client.post(f"/api/v1/resumes/{missing_id}/parse")
    assert res_parse.status_code == 404

    res_extract = client.post(f"/api/v1/resumes/{missing_id}/extract")
    assert res_extract.status_code == 404

    res_lib = client.get(f"/api/v1/resumes/library/{missing_id}")
    assert res_lib.status_code == 404


# -----------------------------------------------------------------------------
# 15. Path traversal protection
# -----------------------------------------------------------------------------
def test_path_traversal_protection(client):
    traversal_ids = [
        "../../etc/passwd",
        "..%2F..%2Fetc%2Fpasswd",
        "../file",
        "nested/path/to/file",
        "invalid_hex_string_too_short",
    ]
    for tid in traversal_ids:
        res = client.get(f"/api/v1/resumes/library/{tid}")
        assert res.status_code in [400, 404]

    with pytest.raises(ValueError):
        storage_service.validate_file_id("../../etc/passwd")


# -----------------------------------------------------------------------------
# 16. Job Matcher regression
# -----------------------------------------------------------------------------
def test_job_matcher_regression(client):
    pdf = create_synthetic_pdf(
        skills="Python, SQL, FastAPI, Docker, PostgreSQL",
    )
    up = client.post("/api/v1/resumes/upload", files={"file": ("matcher_resume.pdf", pdf, "application/pdf")})
    file_id = up.json()["file_id"]

    client.post(f"/api/v1/resumes/{file_id}/parse")

    jd = (
        "We are looking for a Python Backend Developer.\n"
        "Required Skills: Python, FastAPI, SQL, PostgreSQL.\n"
        "Preferred: Docker.\n"
        "Experience: 2+ years backend engineering.\n"
        "Education: Bachelor's degree in Computer Science."
    )

    match_res = client.post(
        "/api/v1/jobs/match",
        json={
            "file_id": file_id,
            "job_description": jd,
            "job_title": "Python Developer",
            "company": "TechCorp",
            "location": "Remote",
        },
    )
    assert match_res.status_code == 200
    match_data = match_res.json()
    assert match_data["overall_score"] > 0
    assert "match_score" in match_data
    assert "matched_skills" in match_data


# -----------------------------------------------------------------------------
# 17. Existing onboarding regression
# -----------------------------------------------------------------------------
def test_existing_onboarding_regression(client):
    status_res = client.get("/api/v1/onboarding/status")
    assert status_res.status_code == 200

    onboard_payload = {
        "full_name": "Alex Morgan",
        "career_status": "Fresher",
        "highest_education": "Bachelor's",
        "degree": "B.Tech Computer Science",
        "institution": "MIT",
        "graduation_year": 2026,
        "primary_target_role": "Python Developer",
        "preferred_job_type": "Full-time",
        "preferred_work_mode": "Remote",
        "preferred_locations": ["San Francisco"],
    }

    create_res = client.post("/api/v1/onboarding/profile", json=onboard_payload)
    assert create_res.status_code == 201
    assert create_res.json()["full_name"] == "Alex Morgan"

    get_res = client.get("/api/v1/onboarding/profile")
    assert get_res.status_code == 200
    assert get_res.json()["full_name"] == "Alex Morgan"
