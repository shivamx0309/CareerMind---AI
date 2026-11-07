"""
CareerMind AI — Phase 5.8: End-to-End Verification Test Suite.

Validates the complete workflow from synthetic PDF resume upload, parsing,
session handling, explainable matching across multiple job descriptions,
error state robustness, and score safety.
"""

import json
import uuid
import pymupdf
import pytest
from fastapi.testclient import TestClient

from main import app
from schemas.matching_schema import (
    JobMatchResponse,
    SkillMatchStatus,
    SkillRequirementType,
    ComponentAvailability,
    MatchScoreBreakdown,
)

client = TestClient(app)


def generate_synthetic_candidate_pdf() -> bytes:
    """Generate a clean, synthetic candidate resume PDF for testing."""
    doc = pymupdf.open()
    page = doc.new_page()

    text = (
        "ALEX REED\n"
        "alex.reed@example.com | +1 555-019-2834 | San Francisco, CA\n"
        "linkedin.com/in/alex-reed | github.com/alexreed-dev\n\n"
        "Professional Summary\n"
        "Software Engineer with hands-on experience in Python backend development, "
        "PostgreSQL databases, and RESTful microservices. Proficient in Docker and Redis.\n\n"
        "Technical Skills\n"
        "Programming: Python, SQL, Java\n"
        "Frameworks & Tools: FastAPI, Django, Flask, Docker, Git, Redis\n"
        "Databases: PostgreSQL, MySQL, SQLite\n\n"
        "Work Experience\n"
        "Backend Developer — CloudScale Systems\n"
        "Jan 2023 – Present\n"
        "• Engineered scalable REST API endpoints using Python and FastAPI.\n"
        "• Optimized PostgreSQL queries and database schemas, reducing query response times by 35%.\n"
        "• Implemented caching layer with Redis to handle 5,000 concurrent user sessions.\n\n"
        "Software Engineering Intern — NextGen Tech\n"
        "Jun 2022 – Dec 2022\n"
        "• Built data ingestion scripts using Python and Pandas.\n"
        "• Integrated Docker container workflows and CI/CD pipelines.\n\n"
        "Projects\n"
        "Distributed Task Queue System\n"
        "Python — Celery — Redis — Docker\n"
        "• Designed an asynchronous task processing queue capable of handling 50k daily background tasks.\n\n"
        "Education\n"
        "Bachelor of Science (Computer Science)\n"
        "2018–2022\n"
        "University of California, Berkeley\n"
    )

    page.insert_text((50, 50), text, fontsize=10)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


# =============================================================================
# 1. Environment & Health Check
# =============================================================================
def test_environment_and_api_docs():
    """Verify that Swagger docs, OpenAPI schema, and root API routes are operational."""
    resp_docs = client.get("/docs")
    assert resp_docs.status_code == 200

    resp_openapi = client.get("/openapi.json")
    assert resp_openapi.status_code == 200
    schema = resp_openapi.json()
    assert "/api/v1/jobs/match" in schema["paths"]
    assert "/api/v1/resumes/upload" in schema["paths"]


# =============================================================================
# 2. Resume Upload & Parsing Lifecycle
# =============================================================================
def test_e2e_resume_upload_and_parse_lifecycle():
    """Verify upload, ID generation, text extraction, and structured parsing."""
    pdf_bytes = generate_synthetic_candidate_pdf()

    # Step 1: Upload PDF (FastAPI returns 201 Created)
    upload_resp = client.post(
        "/api/v1/resumes/upload",
        files={"file": ("alex_reed_resume.pdf", pdf_bytes, "application/pdf")},
    )
    assert upload_resp.status_code == 201
    upload_data = upload_resp.json()
    assert upload_data["success"] is True
    file_id = upload_data["file_id"]
    assert len(file_id) == 32
    assert all(c in "0123456789abcdef" for c in file_id)

    # Step 2: Parse Profile
    parse_resp = client.post(f"/api/v1/resumes/{file_id}/parse")
    assert parse_resp.status_code == 200
    parse_data = parse_resp.json()
    assert parse_data["success"] is True
    candidate = parse_data["candidate"]

    # Verify extracted skills and experience
    assert "Python" in candidate["technical_skills"]["programming_languages"]
    assert "PostgreSQL" in candidate["technical_skills"]["databases"]
    assert len(candidate["experience"]) >= 2
    assert candidate["education"][0]["degree"] == "Bachelor of Science"


# =============================================================================
# 3. Real Job Matching: Python Backend Developer
# =============================================================================
def test_e2e_match_python_backend_job():
    """Test full matching workflow against a realistic Python Backend Developer JD."""
    pdf_bytes = generate_synthetic_candidate_pdf()
    upload_resp = client.post(
        "/api/v1/resumes/upload",
        files={"file": ("resume.pdf", pdf_bytes, "application/pdf")},
    )
    file_id = upload_resp.json()["file_id"]

    python_backend_jd = (
        "We are looking for a skilled Python Backend Developer to join our core engineering team.\n\n"
        "Requirements:\n"
        "- 2+ years of professional software engineering experience.\n"
        "- Strong proficiency in Python, PostgreSQL, Redis, and RESTful APIs.\n"
        "- Experience with Docker, Kubernetes, and microservices architecture.\n"
        "- Bachelor's degree in Computer Science, Software Engineering, or related technical field.\n"
        "- Preferred: Familiarity with Celery, Kafka, and AWS cloud deployment.\n\n"
        "Responsibilities:\n"
        "- Design and maintain high-performance backend microservices.\n"
        "- Write unit tests, optimize SQL queries, and ensure code quality."
    )

    match_payload = {
        "file_id": file_id,
        "job_title": "Python Backend Developer",
        "company": "NovaTech Solutions",
        "location": "Remote",
        "job_description": python_backend_jd,
    }

    match_resp = client.post("/api/v1/jobs/match", json=match_payload)
    assert match_resp.status_code == 200
    data = match_resp.json()

    # Validate with actual Pydantic model
    validated = JobMatchResponse.model_validate(data)

    # 1. Overall Score and Classification (do not hardcode expected match percentages)
    assert validated.overall_score is not None
    assert 0.0 <= validated.overall_score <= 100.0
    assert validated.match_classification in ("Strong Match", "Moderate Match", "Partial Match", "Low Match")

    # 2. Matched Skills Verification
    matched_names = {m.skill for m in validated.matched_skills if m.status in (SkillMatchStatus.EXACT_MATCH, SkillMatchStatus.ALIAS_MATCH)}
    assert "Python" in matched_names
    assert "PostgreSQL" in matched_names
    assert "Redis" in matched_names
    assert "Docker" in matched_names

    # 3. Related Skills Verification (e.g. Docker relates to Kubernetes)
    related_names = {m.skill for m in validated.related_skills}
    # Kubernetes is required in JD; candidate has Docker
    if "Kubernetes" in related_names:
        item = next(m for m in validated.related_skills if m.skill == "Kubernetes")
        assert item.status == SkillMatchStatus.SEMANTICALLY_RELATED
        assert "Docker" in item.candidate_evidence
        assert 0.0 <= item.match_confidence <= 1.0

    # 4. Experience Verification
    exp = validated.experience_match
    assert exp is not None
    assert exp.required_years == 2.0
    assert exp.professional_years >= 2.0
    assert exp.internship_years > 0.0
    assert len(exp.project_evidence) > 0
    # Projects are structured dictionaries
    assert isinstance(exp.project_evidence[0], dict)
    assert "project_name" in exp.project_evidence[0]

    # 5. Education Verification
    edu = validated.education_match
    assert edu is not None
    assert edu.degree_match is True
    assert edu.status == "exact_match"

    # 6. Recommendations Quality Check
    recs = validated.recommendations
    assert len(recs) > 0
    for rec in recs:
        # Recommendations must contain structured action steps
        assert len(rec.suggested_actions) >= 2
        # Must require demonstrable projects before updating profile
        combined_text = " ".join(rec.suggested_actions).lower()
        if "profile" in combined_text or "resume" in combined_text:
            assert "after" in combined_text or "demonstrating" in combined_text or "evidence" in combined_text


# =============================================================================
# 4. Real Job Matching: Data Analyst
# =============================================================================
def test_e2e_match_data_analyst_job():
    """Test full matching workflow against a Data Analyst JD with distinct gaps."""
    pdf_bytes = generate_synthetic_candidate_pdf()
    upload_resp = client.post(
        "/api/v1/resumes/upload",
        files={"file": ("resume.pdf", pdf_bytes, "application/pdf")},
    )
    file_id = upload_resp.json()["file_id"]

    data_analyst_jd = (
        "InsightAnalytics is seeking an enthusiastic Junior Data Analyst to join our team.\n\n"
        "Requirements:\n"
        "- Bachelor's degree in Statistics, Mathematics, Computer Science, or Economics.\n"
        "- Strong proficiency in SQL, Python, Excel, Power BI, and Tableau.\n"
        "- Experience in Exploratory Data Analysis (EDA) and data visualization.\n"
        "- Preferred: Experience with Snowflake, R, and statistical hypothesis testing.\n\n"
        "Responsibilities:\n"
        "- Build dashboards, extract SQL metrics, and deliver weekly KPI presentations."
    )

    match_payload = {
        "file_id": file_id,
        "job_title": "Junior Data Analyst",
        "company": "InsightAnalytics Corp",
        "location": "Hybrid",
        "job_description": data_analyst_jd,
    }

    match_resp = client.post("/api/v1/jobs/match", json=match_payload)
    assert match_resp.status_code == 200
    data = match_resp.json()
    validated = JobMatchResponse.model_validate(data)

    # Candidate has Python and SQL, but lacks Power BI and Tableau
    matched_names = {m.skill for m in validated.matched_skills if m.status == SkillMatchStatus.EXACT_MATCH}
    assert "Python" in matched_names
    assert "SQL" in matched_names

    missing_req_names = set(validated.missing_required_skills)
    # Power BI and Tableau should be identified as missing required skills
    assert "Power BI" in missing_req_names or "Tableau" in missing_req_names or "Excel" in missing_req_names


# =============================================================================
# 5. Score Safety: Unassessable State Handling
# =============================================================================
def test_unassessable_score_safety():
    """Verify that when unassessable, overall_score is null and never serialized as 0.0."""
    pdf_bytes = generate_synthetic_candidate_pdf()
    upload_resp = client.post(
        "/api/v1/resumes/upload",
        files={"file": ("resume.pdf", pdf_bytes, "application/pdf")},
    )
    file_id = upload_resp.json()["file_id"]

    # Construct an unassessable response scenario
    from matching_engine import score_calculator, matching_service
    from schemas.matching_schema import ComponentScore

    def mock_all_unavailable(*args, **kwargs):
        comps = {
            cname: ComponentScore(
                component_name=cname,
                availability=ComponentAvailability.UNAVAILABLE,
                raw_score=None,
                base_weight=0.2,
                normalized_weight=0.0,
                weighted_contribution=0.0,
                evidence=[],
                reason="Unassessed dimension",
            )
            for cname in ("required_skills", "preferred_skills", "experience", "education", "lexical_relevance")
        }
        return MatchScoreBreakdown(
            overall_score=None,
            match_classification="Not assessable",
            components=comps,
            weight_normalization_applied=False,
            explanation="No scoring components were available for evaluation. The match is not assessable.",
        )

    # Monkeypatch for this test
    original_calc = matching_service.calculate_match_score
    try:
        matching_service.calculate_match_score = mock_all_unavailable

        resp = client.post(
            "/api/v1/jobs/match",
            json={
                "file_id": file_id,
                "job_description": "We are seeking software engineers to build great products for our clients.",
            },
        )
        assert resp.status_code == 200
        raw_text = resp.text

        # 1. Null check in raw JSON (no 0% or numeric substitution)
        assert '"overall_score":null' in raw_text.replace(" ", "")
        assert '"match_classification":"Not assessable"' in raw_text

        # 2. Parsed JSON check
        body = resp.json()
        assert body["overall_score"] is None
        assert body["match_classification"] == "Not assessable"
        assert body["match_score"]["overall_score"] is None
        assert body["match_score"]["match_classification"] == "Not assessable"

        # 3. Pydantic validation
        validated = JobMatchResponse.model_validate(body)
        assert validated.overall_score is None
        assert validated.match_classification == "Not assessable"
    finally:
        matching_service.calculate_match_score = original_calc


# =============================================================================
# 6. Error Scenarios Robustness
# =============================================================================
def test_error_scenarios_robustness():
    """Verify HTTP status codes, error details, and recovery guidance."""
    # 1. Invalid file_id format (HTTP 400)
    resp_invalid_id = client.post(
        "/api/v1/jobs/match",
        json={"file_id": "not-a-valid-hex-uuid", "job_description": "Valid job description of at least 50 characters long."},
    )
    assert resp_invalid_id.status_code == 400
    assert "32-character" in resp_invalid_id.json()["detail"]

    # 2. Non-existent file_id (HTTP 404)
    missing_id = uuid.uuid4().hex
    resp_missing = client.post(
        "/api/v1/jobs/match",
        json={"file_id": missing_id, "job_description": "Valid job description of at least 50 characters long."},
    )
    assert resp_missing.status_code == 404
    assert "not found" in resp_missing.json()["detail"].lower()

    # 3. Job description too short < 50 chars (HTTP 422)
    resp_short = client.post(
        "/api/v1/jobs/match",
        json={"file_id": uuid.uuid4().hex, "job_description": "Too short"},
    )
    assert resp_short.status_code == 422
    assert "50 characters" in str(resp_short.json()["detail"])

    # 4. Job description too long > 30,000 chars (HTTP 422)
    giant_jd = "Python Developer " * 2500  # ~42,500 chars
    resp_long = client.post(
        "/api/v1/jobs/match",
        json={"file_id": uuid.uuid4().hex, "job_description": giant_jd},
    )
    assert resp_long.status_code == 422
    assert "30,000" in str(resp_long.json()["detail"])

    # 5. Empty text PDF extraction (HTTP 422)
    blank_doc = pymupdf.open()
    blank_doc.new_page()
    blank_bytes = blank_doc.tobytes()
    blank_doc.close()

    upload_blank = client.post(
        "/api/v1/resumes/upload",
        files={"file": ("blank.pdf", blank_bytes, "application/pdf")},
    )
    blank_id = upload_blank.json()["file_id"]

    resp_blank_match = client.post(
        "/api/v1/jobs/match",
        json={"file_id": blank_id, "job_description": "Valid job description of at least 50 characters long."},
    )
    assert resp_blank_match.status_code == 422
    assert "No readable text" in resp_blank_match.json()["detail"]
