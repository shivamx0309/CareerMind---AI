"""
CareerMind AI — Phase 2: Skill Gap Analysis Engine Unit & Integration Tests.

Comprehensive test suite verifying:
1. Standard role benchmark retrieval (/skills/roles)
2. Exact and alias skill matching (confidence 1.0)
3. Semantically related skill classification (confidence 0.6)
4. Missing skill identification (required vs preferred)
5. Deterministic scoring calculation
6. Category breakdown aggregation
7. Default and specific resume selection
8. Error handling: unparsed resume (422), invalid role (400), not found (404)
9. Boundary states: zero candidate skills, insufficient benchmark
10. Report persistence, listing, retrieval, and deletion
11. Regressions: Resume Library and Job Matcher remain unaffected
"""

import json
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database.base import Base
from database.session import get_db
from database.models.career_profile import CareerProfile
from database.models.resume_record import ResumeRecord
from database.models.skill_gap_report import SkillGapReport
from schemas.candidate_schema import (
    CandidateProfile,
    PersonalInformation,
    TechnicalSkills,
    ExperienceEntry,
    ProjectEntry,
    CertificationEntry,
)
from schemas.career_profile_schema import CareerProfileCreate
from services import (
    storage_service,
    resume_library_service,
    career_profile_service,
    role_benchmark_service,
    skill_gap_service,
)
from services.role_benchmark_service import RoleBenchmark, BenchmarkSkill
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
    """Clean in-memory DB and isolated upload directory for every test."""
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


def create_candidate_with_skills(
    programming_languages=None,
    frontend=None,
    backend=None,
    databases=None,
    tools=None,
    data_analytics=None,
    machine_learning=None,
    deep_learning=None,
    cloud_devops=None,
    other=None,
) -> CandidateProfile:
    """Helper to assemble a CandidateProfile with specific technical skills."""
    return CandidateProfile(
        personal_information=PersonalInformation(
            full_name="Alex Mercer",
            email="alex.mercer@example.com",
            phone="+1234567890",
            location="Seattle, WA",
        ),
        technical_skills=TechnicalSkills(
            programming_languages=programming_languages or [],
            frontend=frontend or [],
            backend=backend or [],
            databases=databases or [],
            tools=tools or [],
            data_analytics=data_analytics or [],
            machine_learning=machine_learning or [],
            deep_learning=deep_learning or [],
            cloud_devops=cloud_devops or [],
            other=other or [],
        ),
        experience=[],
        projects=[],
        certifications=[],
    )


def setup_user_and_resume(db, candidate: CandidateProfile, is_default: bool = True, file_id: str = "11112222333344445555666677778888"):
    """Helper to seed CareerProfile and parsed ResumeRecord."""
    profile = career_profile_service.get_or_create_local_career_profile(db)
    record = resume_library_service.register_uploaded_resume(
        db=db,
        career_profile_id=profile.id,
        file_id=file_id,
        original_filename="alex_resume.pdf",
        file_size=10240,
        display_name="Alex Master Resume",
    )
    record.is_default = is_default
    db.commit()
    resume_library_service.persist_parsed_candidate_profile(db, record.id, candidate)
    return profile, record


# =============================================================================
# 1. Benchmark Catalog Tests
# =============================================================================

def test_list_role_benchmarks_endpoint(client):
    """GET /api/v1/skills/roles returns all 8 standard role benchmarks."""
    response = client.get("/api/v1/skills/roles")
    assert response.status_code == 200
    roles = response.json()
    assert len(roles) == 8

    role_ids = [r["role_id"] for r in roles]
    expected_roles = [
        "sde",
        "frontend_developer",
        "backend_developer",
        "full_stack_developer",
        "data_analyst",
        "data_scientist",
        "machine_learning_engineer",
        "python_developer",
    ]
    for exp in expected_roles:
        assert exp in role_ids

    # Inspect structure of first benchmark (sde)
    sde = next(r for r in roles if r["role_id"] == "sde")
    assert sde["title"] == "Software Development Engineer (SDE)"
    assert sde["domain"] == "Software Engineering"
    assert sde["required_skills_count"] > 0
    assert sde["preferred_skills_count"] > 0
    assert "Python" in sde["required_skills"]
    assert "Docker" in sde["preferred_skills"]


# =============================================================================
# 2. Skill Matching & Evaluation Tests (Exact, Alias, Related, Missing)
# =============================================================================

def test_exact_and_alias_matches(client, db_session):
    """
    Exact matches and known aliases earn confidence 1.0.
    Python Developer benchmark requires: Python, FastAPI, SQL, PostgreSQL, REST API, Git.
    Candidate has: Python, FastAPI, SQL, Postgres (alias for PostgreSQL), REST API, Git.
    """
    candidate = create_candidate_with_skills(
        programming_languages=["Python"],
        backend=["FastAPI", "REST API"],
        databases=["SQL", "Postgres"],  # Postgres is canonical alias for PostgreSQL
        tools=["Git"],
    )
    _, resume = setup_user_and_resume(db_session, candidate)

    response = client.post(
        "/api/v1/skills/analyze",
        json={"target_role": "python_developer", "resume_id": resume.id},
    )
    assert response.status_code == 201
    data = response.json()

    assert data["target_role"] == "python_developer"
    assert data["analysis_status"] == "completed"
    assert data["matched_required_skills_count"] == 6
    assert data["missing_required_skills_count"] == 0

    # Verify alias match detection
    matched_names = {item["skill_name"]: item for item in data["matched_skills"]}
    assert "PostgreSQL" in matched_names
    assert matched_names["PostgreSQL"]["match_confidence"] == 1.0
    assert matched_names["PostgreSQL"]["status"] in ("exact_match", "alias_match")


def test_semantically_related_skill_classification(client, db_session):
    """
    Semantically related skill from same cluster earns confidence 0.6 and is marked 'semantically_related'.
    Python Developer benchmark requires FastAPI.
    Candidate only has Django (in the 'Python Web Frameworks' cluster).
    """
    candidate = create_candidate_with_skills(
        programming_languages=["Python"],
        backend=["Django"],  # Django is related to FastAPI
        databases=["SQL"],
        tools=["Git"],
    )
    _, resume = setup_user_and_resume(db_session, candidate)

    response = client.post(
        "/api/v1/skills/analyze",
        json={"target_role": "python_developer", "resume_id": resume.id},
    )
    assert response.status_code == 201
    data = response.json()

    # FastAPI should appear in related_skills with confidence 0.6
    related_names = {item["skill_name"]: item for item in data["related_skills"]}
    assert "FastAPI" in related_names
    assert related_names["FastAPI"]["match_confidence"] == 0.6
    assert related_names["FastAPI"]["status"] == "semantically_related"
    assert related_names["FastAPI"]["importance"] == "required"


def test_missing_required_and_preferred_skills(client, db_session):
    """
    Skills neither matched nor related are flagged in missing_required_skills and missing_preferred_skills.
    """
    # Candidate only has Python and Git
    candidate = create_candidate_with_skills(
        programming_languages=["Python"],
        tools=["Git"],
    )
    _, resume = setup_user_and_resume(db_session, candidate)

    response = client.post(
        "/api/v1/skills/analyze",
        json={"target_role": "python_developer", "resume_id": resume.id},
    )
    assert response.status_code == 201
    data = response.json()

    assert "PostgreSQL" in data["missing_required_skills"]
    assert "REST API" in data["missing_required_skills"]
    assert "Docker" in data["missing_preferred_skills"]
    assert "Redis" in data["missing_preferred_skills"]


# =============================================================================
# 3. Deterministic Scoring & Category Breakdown Tests
# =============================================================================

def test_deterministic_scoring_formula(client, db_session):
    """
    Verifies that the overall_score strictly matches the mathematical formula:
    score = round((sum(confidence * weight) / sum(weight)) * 100, 1)
    """
    # Python Developer has:
    # 6 required (weight 1.0): Python, FastAPI, SQL, PostgreSQL, REST API, Git
    # 5 preferred (weight 0.5): Django, Flask, Docker, Redis, Linux
    # Total weights = 6 * 1.0 + 5 * 0.5 = 8.5
    #
    # Candidate skills:
    # Python (exact, 1.0 * 1.0 = 1.0)
    # Git (exact, 1.0 * 1.0 = 1.0)
    # Django (in preferred: exact 1.0 * 0.5 = 0.5; also relates to FastAPI and Flask in Python Web Frameworks cluster:
    #         FastAPI: 0.6 * 1.0 = 0.6; Flask: 0.6 * 0.5 = 0.3)
    # Docker (preferred: exact 1.0 * 0.5 = 0.5)
    # Total weighted score = 1.0 + 1.0 + 0.6 + 0.5 + 0.5 + 0.3 = 3.9
    # Expected overall_score = round((3.9 / 8.5) * 100, 1) = 45.9
    candidate = create_candidate_with_skills(
        programming_languages=["Python"],
        backend=["Django"],
        tools=["Git"],
        cloud_devops=["Docker"],
    )
    _, resume = setup_user_and_resume(db_session, candidate)

    response = client.post(
        "/api/v1/skills/analyze",
        json={"target_role": "python_developer", "resume_id": resume.id},
    )
    assert response.status_code == 201
    data = response.json()

    assert data["overall_score"] == 45.9
    # Required coverage: 2 exact/alias out of 6 = 33.3%
    assert data["required_coverage_percentage"] == 33.3


def test_category_breakdown_metrics(client, db_session):
    """Category breakdown groups correctly by technical category and calculates coverage."""
    candidate = create_candidate_with_skills(
        programming_languages=["Python", "TypeScript"],
        frontend=["React", "HTML5", "CSS3"],
        tools=["Git"],
    )
    _, resume = setup_user_and_resume(db_session, candidate)

    response = client.post(
        "/api/v1/skills/analyze",
        json={"target_role": "frontend_developer", "resume_id": resume.id},
    )
    assert response.status_code == 201
    data = response.json()

    breakdowns = {c["category"]: c for c in data["category_breakdown"]}
    assert "frontend" in breakdowns
    frontend_cat = breakdowns["frontend"]
    assert frontend_cat["total_skills"] > 0
    assert frontend_cat["matched_count"] >= 3
    assert frontend_cat["coverage_percentage"] > 0


# =============================================================================
# 4. Resume Selection & Boundary Tests
# =============================================================================

def test_default_resume_automatic_selection(client, db_session):
    """When resume_id is omitted, the user's default resume is automatically selected."""
    candidate1 = create_candidate_with_skills(programming_languages=["Python"])
    candidate2 = create_candidate_with_skills(programming_languages=["Java", "C++"])

    profile = career_profile_service.get_or_create_local_career_profile(db_session)
    rec1 = resume_library_service.register_uploaded_resume(
        db=db_session,
        career_profile_id=profile.id,
        file_id="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        original_filename="resume_a.pdf",
        file_size=1000,
    )
    rec1.is_default = True
    db_session.commit()
    resume_library_service.persist_parsed_candidate_profile(db_session, rec1.id, candidate1)

    rec2 = resume_library_service.register_uploaded_resume(
        db=db_session,
        career_profile_id=profile.id,
        file_id="bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        original_filename="resume_b.pdf",
        file_size=1000,
    )
    rec2.is_default = False
    db_session.commit()
    resume_library_service.persist_parsed_candidate_profile(db_session, rec2.id, candidate2)

    # Omit resume_id
    response = client.post(
        "/api/v1/skills/analyze",
        json={"target_role": "python_developer"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["resume_record_id"] == rec1.id


def test_unparsed_resume_returns_422(client, db_session):
    """Analysis fails with 422 if the target resume has not been parsed."""
    profile = career_profile_service.get_or_create_local_career_profile(db_session)
    rec = resume_library_service.register_uploaded_resume(
        db=db_session,
        career_profile_id=profile.id,
        file_id="cccccccccccccccccccccccccccccccc",
        original_filename="unparsed.pdf",
        file_size=1000,
    )
    # Ensure parsing_status is pending
    rec.parsing_status = "pending"
    db_session.commit()

    response = client.post(
        "/api/v1/skills/analyze",
        json={"target_role": "python_developer", "resume_id": rec.id},
    )
    assert response.status_code == 422
    assert "has not been parsed" in response.json()["detail"]


def test_invalid_target_role_returns_400(client, db_session):
    """Analysis with non-existent target role returns 400 Bad Request."""
    candidate = create_candidate_with_skills(programming_languages=["Python"])
    _, resume = setup_user_and_resume(db_session, candidate)

    response = client.post(
        "/api/v1/skills/analyze",
        json={"target_role": "non_existent_role_xyz", "resume_id": resume.id},
    )
    assert response.status_code == 400
    assert "not supported" in response.json()["detail"]


def test_resume_not_found_returns_404(client, db_session):
    """Analysis with unknown resume_id returns 404 Not Found."""
    career_profile_service.get_or_create_local_career_profile(db_session)

    response = client.post(
        "/api/v1/skills/analyze",
        json={"target_role": "python_developer", "resume_id": "non-existent-uuid"},
    )
    assert response.status_code == 404


def test_no_candidate_skills_boundary(client, db_session):
    """Resume with 0 detectable skills yields 0 score and 'no_candidate_skills' status."""
    candidate = create_candidate_with_skills()  # All categories empty
    _, resume = setup_user_and_resume(db_session, candidate)

    response = client.post(
        "/api/v1/skills/analyze",
        json={"target_role": "sde", "resume_id": resume.id},
    )
    assert response.status_code == 201
    data = response.json()

    assert data["analysis_status"] == "no_candidate_skills"
    assert data["overall_score"] == 0.0
    assert data["required_coverage_percentage"] == 0.0


def test_insufficient_benchmark_boundary(client, db_session, monkeypatch):
    """Benchmark with 0 required skills yields None score and 'insufficient_benchmark' status."""
    candidate = create_candidate_with_skills(programming_languages=["Python"])
    _, resume = setup_user_and_resume(db_session, candidate)

    empty_bm = RoleBenchmark(
        role_id="empty_role",
        title="Empty Role",
        description="Benchmark with no required skills",
        domain="Testing",
        required_skills=[],
        preferred_skills=[BenchmarkSkill(skill_name="Python", category="programming_languages", importance="preferred", weight=0.5)],
    )

    with patch("services.skill_gap_service.get_role_benchmark", return_value=empty_bm):
        response = client.post(
            "/api/v1/skills/analyze",
            json={"target_role": "empty_role", "resume_id": resume.id},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["analysis_status"] == "insufficient_benchmark"
        assert data["overall_score"] is None
        assert data["required_coverage_percentage"] is None


# =============================================================================
# 5. Persistence, Historical Reports & Deletion Lifecycle Tests
# =============================================================================

def test_report_lifecycle_persistence_listing_and_deletion(client, db_session):
    """
    Test end-to-end report persistence:
    1. POST /skills/analyze creates persistent SkillGapReport in DB.
    2. GET /skills/reports lists historical reports.
    3. GET /skills/reports/{id} fetches full report with resume_name.
    4. DELETE /skills/reports/{id} removes report (204).
    5. GET /skills/reports/{id} after deletion returns 404.
    """
    candidate = create_candidate_with_skills(
        programming_languages=["Python"],
        backend=["FastAPI"],
        tools=["Git"],
    )
    _, resume = setup_user_and_resume(db_session, candidate)

    # 1. Create Report
    post_res = client.post(
        "/api/v1/skills/analyze",
        json={"target_role": "python_developer", "resume_id": resume.id},
    )
    assert post_res.status_code == 201
    created = post_res.json()
    report_id = created["id"]
    assert created["resume_name"] == "Alex Master Resume"

    # 2. List Reports
    list_res = client.get("/api/v1/skills/reports")
    assert list_res.status_code == 200
    reports = list_res.json()
    assert len(reports) >= 1
    assert any(r["id"] == report_id for r in reports)

    # 3. Retrieve Report by ID
    get_res = client.get(f"/api/v1/skills/reports/{report_id}")
    assert get_res.status_code == 200
    detail = get_res.json()
    assert detail["id"] == report_id
    assert detail["target_role"] == "python_developer"
    assert detail["role_title"] == "Python Developer"
    assert detail["resume_name"] == "Alex Master Resume"

    # 4. Delete Report
    del_res = client.delete(f"/api/v1/skills/reports/{report_id}")
    assert del_res.status_code == 204

    # 5. Verify Deletion
    del_verify = client.get(f"/api/v1/skills/reports/{report_id}")
    assert del_verify.status_code == 404

    # Deleting non-existent report returns 404
    del_again = client.delete(f"/api/v1/skills/reports/{report_id}")
    assert del_again.status_code == 404


# =============================================================================
# 6. Non-Regression Tests: Resume Library & Job Matcher Unaffected
# =============================================================================

def test_resume_library_remains_functional(client, db_session):
    """Resume library endpoints continue to function without regressions."""
    candidate = create_candidate_with_skills(programming_languages=["Python"])
    setup_user_and_resume(db_session, candidate)

    response = client.get("/api/v1/resumes/library")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["display_name"] == "Alex Master Resume"


def test_job_matcher_remains_functional(client, db_session):
    """Job matching endpoint continues to function without regressions."""
    import pymupdf

    candidate = create_candidate_with_skills(
        programming_languages=["Python"],
        backend=["FastAPI"],
    )
    _, resume = setup_user_and_resume(db_session, candidate)

    # Valid PDF on disk for jobs endpoint
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text(
        (50, 72),
        "Alex Mercer\nEmail: alex@example.com\nSkills: Python, FastAPI, SQL, Git\nExperience: Python Developer (2022 - Present)",
        fontsize=11,
    )
    file_path = storage_service.get_file_path(resume.file_id, base_dir=resume_endpoint.UPLOAD_DIR)
    file_path.write_bytes(doc.tobytes())

    jd_payload = {
        "file_id": resume.file_id,
        "job_title": "Python Backend Engineer",
        "job_description": (
            "We are looking for a Python Backend Engineer with strong FastAPI and Python skills. "
            "Must have experience with SQL databases and Git."
        ),
    }

    response = client.post(
        "/api/v1/jobs/match",
        json=jd_payload,
    )
    assert response.status_code == 200
    match_data = response.json()
    assert "overall_score" in match_data
    assert match_data["overall_score"] > 0
