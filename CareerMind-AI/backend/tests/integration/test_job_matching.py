"""
Integration tests for the Job Matching API (Phase 5.6):
POST /api/v1/jobs/match

Covers:
1. Successful end-to-end job match.
2. Exact skill match.
3. Related skill match.
4. Missing required skills.
5. Missing preferred skills.
6. Experience assessment integration.
7. Education assessment integration.
8. Explainable score integration.
9. Recommendation integration.
10. Invalid resume file ID (HTTP 400).
11. Missing resume file (HTTP 404).
12. Corrupt PDF document (HTTP 422).
13. Empty or invalid JD text (HTTP 422).
14. Oversized JD text (HTTP 422).
15. Missing candidate profile / empty text PDF (HTTP 422).
16. No education requirement in JD (weight re-normalization).
17. No experience requirement in JD.
18. All scoring components unavailable handling.
19. No duplicate skill evidence or recommendations.
20. Response schema validation with Pydantic model.
"""

import uuid
import pymupdf
import pytest
from fastapi.testclient import TestClient

from main import app
from api.v1.endpoints import resume as resume_endpoint
from api.v1.endpoints import jobs as jobs_endpoint
from schemas.matching_schema import JobMatchResponse, SkillMatchStatus

client = TestClient(app)


def create_realistic_candidate_pdf() -> bytes:
    """Create a realistic in-memory candidate resume PDF for testing."""
    document = pymupdf.open()
    page = document.new_page()

    content = (
        "SHIVAM KUMAR SINGH\n"
        "Phone: +91 8887602317\n"
        "Email: edu.shivam0903@gmail.com\n"
        "LinkedIn: https://www.linkedin.com/in/shivam-kumar-singh-2b082a332\n"
        "GitHub: https://github.com/shivamx0309\n"
        "\n"
        "Professional Summary\n"
        "Computer Science Engineering student skilled in SQL, Python, Excel, Power BI, and Data Analytics. "
        "Passionate about transforming data into actionable business insights.\n"
        "\n"
        "Technical Skills\n"
        "Programming: Python, SQL, Java\n"
        "Analytics: Pandas, NumPy, Power BI, Excel, EDA\n"
        "Databases: PostgreSQL, MySQL, MongoDB\n"
        "Machine Learning: Scikit-learn, Regression, Classification\n"
        "Tools: Git, GitHub, VS Code, Jupyter Notebook\n"
        "Cloud & Web: AWS, Django, HTML, CSS\n"
        "\n"
        "Work Experience\n"
        "Tech Innovation Associate — Humppl\n"
        "Jun 2026 – Present\n"
        "• Developed and enhanced CRM modules using Next.js, TypeScript, Tailwind CSS and Supabase.\n"
        "• Worked with PostgreSQL for database operations.\n"
        "\n"
        "Projects\n"
        "Employee Attrition Prediction Model\n"
        "Python — Pandas — NumPy — Scikit-learn — Machine Learning\n"
        "• Developed an employee attrition prediction model using Python and Scikit-learn.\n"
        "• Repository: https://github.com/shivamx0309/Employee-Attrition-Analysis\n"
        "\n"
        "Education\n"
        "Bachelor of Engineering (Computer Science Engineering)\n"
        "2022–2026\n"
        "Institute of Engineering and Technology, Agra\n"
        "\n"
        "Certifications\n"
        "• Completed Accenture Data Analytics & Visualization Job Simulation.\n"
        "• AWS Certified Solutions Architect\n"
    )

    page.insert_text((50, 50), content, fontsize=10)
    pdf_bytes = document.tobytes()
    document.close()
    return pdf_bytes


def create_empty_text_pdf() -> bytes:
    """Create a valid PDF with no extractable text."""
    document = pymupdf.open()
    document.new_page()
    pdf_bytes = document.tobytes()
    document.close()
    return pdf_bytes


@pytest.fixture
def mock_upload_env(tmp_path, monkeypatch):
    """Setup temporary uploads directory and mock both endpoint references."""
    monkeypatch.setattr(resume_endpoint, "UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(jobs_endpoint, "UPLOAD_DIR", tmp_path)
    return tmp_path


# ---------------------------------------------------------------------------
# 1. Successful End-to-End Match
# ---------------------------------------------------------------------------
def test_successful_end_to_end_job_match(mock_upload_env):
    """Verify complete match pipeline returns 200 with all components populated."""
    file_id = uuid.uuid4().hex
    pdf_file = mock_upload_env / f"{file_id}.pdf"
    pdf_file.write_bytes(create_realistic_candidate_pdf())

    jd_payload = {
        "file_id": file_id,
        "job_title": "Backend Python Developer",
        "company": "DataCorp",
        "location": "Remote",
        "job_description": (
            "We are seeking a Backend Python Developer to build modern cloud applications.\n"
            "Requirements:\n"
            "- 2+ years of professional experience in software engineering.\n"
            "- Strong proficiency in Python, SQL, and PostgreSQL.\n"
            "- Bachelor's degree in Computer Science or related technical discipline.\n"
            "Preferred Qualifications:\n"
            "- Experience with AWS and Redis caching.\n"
            "Responsibilities:\n"
            "- Design, develop, and maintain backend microservices and REST APIs.\n"
            "- Optimize PostgreSQL database queries and schemas.\n"
        ),
    }

    response = client.post("/api/v1/jobs/match", json=jd_payload)
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["file_id"] == file_id
    assert data["parsed_job"]["job_title"] == "Backend Python Developer"
    # Privacy check: name and PII are stripped from summary
    assert "name" not in data["candidate_summary"]
    assert data["candidate_summary"]["total_skills_count"] > 0
    assert data["overall_score"] is not None
    assert 0.0 <= data["overall_score"] <= 100.0
    assert data["match_classification"] in ("Strong Match", "Moderate Match", "Partial Match", "Low Match")
    assert len(data["matched_skills"]) > 0
    assert data["match_score"] is not None
    assert data["metadata"]["engine_version"] == "5.6.0"


# ---------------------------------------------------------------------------
# 2. Exact Skill Match Integration
# ---------------------------------------------------------------------------
def test_exact_skill_match_integration(mock_upload_env):
    """Verify exact and canonical alias skills are classified with 1.0 confidence."""
    file_id = uuid.uuid4().hex
    (mock_upload_env / f"{file_id}.pdf").write_bytes(create_realistic_candidate_pdf())

    jd_payload = {
        "file_id": file_id,
        "job_description": (
            "Looking for a Python Developer who knows SQL and PostgreSQL.\n"
            "Must have experience designing databases and writing clean backend code."
        ),
    }

    response = client.post("/api/v1/jobs/match", json=jd_payload)
    assert response.status_code == 200
    data = response.json()

    matched_skills_map = {item["skill"]: item for item in data["matched_skills"]}
    assert "Python" in matched_skills_map
    assert matched_skills_map["Python"]["status"] == SkillMatchStatus.EXACT_MATCH.value
    assert matched_skills_map["Python"]["match_confidence"] == 1.0

    assert "PostgreSQL" in matched_skills_map
    assert matched_skills_map["PostgreSQL"]["status"] in (
        SkillMatchStatus.EXACT_MATCH.value,
        SkillMatchStatus.ALIAS_MATCH.value,
    )


# ---------------------------------------------------------------------------
# 3. Related Skill Match Integration
# ---------------------------------------------------------------------------
def test_related_skill_match_integration(mock_upload_env):
    """Verify semantically related skill (FastAPI vs candidate's Django) is surfaced in related_skills."""
    file_id = uuid.uuid4().hex
    (mock_upload_env / f"{file_id}.pdf").write_bytes(create_realistic_candidate_pdf())

    jd_payload = {
        "file_id": file_id,
        "job_description": (
            "Senior Backend Engineer role.\n"
            "Required Skills:\n"
            "- FastAPI framework for high-throughput asynchronous services.\n"
            "- Python and PostgreSQL database modeling.\n"
        ),
    }

    response = client.post("/api/v1/jobs/match", json=jd_payload)
    assert response.status_code == 200
    data = response.json()

    related_names = [item["skill"] for item in data["related_skills"]]
    assert "FastAPI" in related_names
    fastapi_item = next(item for item in data["related_skills"] if item["skill"] == "FastAPI")
    assert fastapi_item["status"] == SkillMatchStatus.SEMANTICALLY_RELATED.value
    assert "Django" in fastapi_item["candidate_evidence"]


# ---------------------------------------------------------------------------
# 4. Missing Required Skills Integration
# ---------------------------------------------------------------------------
def test_missing_required_skills_integration(mock_upload_env):
    """Verify unevidenced required skills are placed in missing_required_skills."""
    file_id = uuid.uuid4().hex
    (mock_upload_env / f"{file_id}.pdf").write_bytes(create_realistic_candidate_pdf())

    jd_payload = {
        "file_id": file_id,
        "job_description": (
            "Platform Engineer position.\n"
            "Required Skills:\n"
            "- Kubernetes cluster administration.\n"
            "- Golang systems programming.\n"
            "- Python scripting."
        ),
    }

    response = client.post("/api/v1/jobs/match", json=jd_payload)
    assert response.status_code == 200
    data = response.json()

    assert "Kubernetes" in data["missing_required_skills"]
    assert "Go" in data["missing_required_skills"]
    assert "Python" not in data["missing_required_skills"]


# ---------------------------------------------------------------------------
# 5. Missing Preferred Skills Integration
# ---------------------------------------------------------------------------
def test_missing_preferred_skills_integration(mock_upload_env):
    """Verify unevidenced preferred skills appear in missing_preferred_skills."""
    file_id = uuid.uuid4().hex
    (mock_upload_env / f"{file_id}.pdf").write_bytes(create_realistic_candidate_pdf())

    jd_payload = {
        "file_id": file_id,
        "job_description": (
            "Data Engineer role requiring Python and SQL.\n"
            "Preferred Qualifications:\n"
            "- Experience with Snowflake data warehousing.\n"
            "- Terraform infrastructure automation."
        ),
    }

    response = client.post("/api/v1/jobs/match", json=jd_payload)
    assert response.status_code == 200
    data = response.json()

    assert "Snowflake" in data["missing_preferred_skills"]
    assert "Terraform" in data["missing_preferred_skills"]


# ---------------------------------------------------------------------------
# 6. Experience Assessment Integration
# ---------------------------------------------------------------------------
def test_experience_assessment_integration(mock_upload_env):
    """Verify experience assessment integrates tenure, projects, and responsibilities."""
    file_id = uuid.uuid4().hex
    (mock_upload_env / f"{file_id}.pdf").write_bytes(create_realistic_candidate_pdf())

    jd_payload = {
        "file_id": file_id,
        "job_description": (
            "Senior Software Engineer role.\n"
            "Requires at least 5 years of commercial software engineering experience.\n"
            "Required Skills: Python, SQL, PostgreSQL."
        ),
    }

    response = client.post("/api/v1/jobs/match", json=jd_payload)
    assert response.status_code == 200
    data = response.json()

    exp = data["experience_match"]
    assert exp is not None
    assert exp["required_years"] == 5.0
    assert exp["assessment"] in ("below_requirement", "partial")
    assert "5" in exp["explanation"]


# ---------------------------------------------------------------------------
# 7. Education Assessment Integration
# ---------------------------------------------------------------------------
def test_education_assessment_integration(mock_upload_env):
    """Verify education matching detects Bachelor of Engineering in Computer Science."""
    file_id = uuid.uuid4().hex
    (mock_upload_env / f"{file_id}.pdf").write_bytes(create_realistic_candidate_pdf())

    jd_payload = {
        "file_id": file_id,
        "job_description": (
            "Software Engineer role.\n"
            "Education: Bachelor's degree in Computer Science is required.\n"
            "Required Skills: Python, PostgreSQL."
        ),
    }

    response = client.post("/api/v1/jobs/match", json=jd_payload)
    assert response.status_code == 200
    data = response.json()

    edu = data["education_match"]
    assert edu is not None
    assert edu["status"] == "exact_match"
    assert edu["degree_match"] is True
    assert edu["field_match"] is True


# ---------------------------------------------------------------------------
# 8. Explainable Score Integration
# ---------------------------------------------------------------------------
def test_explainable_score_integration(mock_upload_env):
    """Verify explainable score breakdown and weighted contribution consistency."""
    file_id = uuid.uuid4().hex
    (mock_upload_env / f"{file_id}.pdf").write_bytes(create_realistic_candidate_pdf())

    jd_payload = {
        "file_id": file_id,
        "job_description": (
            "Backend Engineer.\n"
            "Required: Python, SQL, PostgreSQL.\n"
            "Preferred: AWS, Redis.\n"
            "Experience: 2+ years experience.\n"
            "Education: Bachelor's in Computer Science."
        ),
    }

    response = client.post("/api/v1/jobs/match", json=jd_payload)
    assert response.status_code == 200
    data = response.json()

    score_data = data["match_score"]
    assert score_data is not None
    components = score_data["components"]

    # Verify all 5 components are present
    assert "required_skills" in components
    assert "preferred_skills" in components
    assert "experience" in components
    assert "education" in components
    assert "lexical_relevance" in components

    # Verify weighted contributions sum up to overall_score
    contrib_sum = sum(
        c["weighted_contribution"] for c in components.values() if c["weighted_contribution"] is not None
    )
    assert pytest.approx(contrib_sum, abs=0.2) == data["overall_score"]


# ---------------------------------------------------------------------------
# 9. Recommendation Integration
# ---------------------------------------------------------------------------
def test_recommendation_integration(mock_upload_env):
    """Verify actionable recommendations are generated for missing required skills and gaps."""
    file_id = uuid.uuid4().hex
    (mock_upload_env / f"{file_id}.pdf").write_bytes(create_realistic_candidate_pdf())

    jd_payload = {
        "file_id": file_id,
        "job_description": (
            "Full Stack Developer.\n"
            "Requirements:\n"
            "- Must know Docker containerization.\n"
            "- Python and SQL required.\n"
            "- 4+ years of professional experience."
        ),
    }

    response = client.post("/api/v1/jobs/match", json=jd_payload)
    assert response.status_code == 200
    data = response.json()

    recs = data["recommendations"]
    assert len(recs) > 0
    # Docker is missing required skill -> High priority recommendation
    docker_rec = next((r for r in recs if "Docker" in r["related_requirement"]), None)
    assert docker_rec is not None
    assert docker_rec["priority"] == "high"
    assert docker_rec["category"] == "required_skill"
    assert len(docker_rec["suggested_actions"]) >= 2


# ---------------------------------------------------------------------------
# 10. Invalid Resume File ID
# ---------------------------------------------------------------------------
def test_invalid_resume_file_id(mock_upload_env):
    """Verify invalid file_id formats return HTTP 400."""
    jd_payload = {
        "file_id": "not-a-valid-hex-uuid",
        "job_description": "We are looking for a Python Developer with SQL experience.",
    }
    response = client.post("/api/v1/jobs/match", json=jd_payload)
    assert response.status_code == 400
    assert "Invalid file ID" in response.json()["detail"]


# ---------------------------------------------------------------------------
# 11. Missing Resume File
# ---------------------------------------------------------------------------
def test_missing_resume_file(mock_upload_env):
    """Verify non-existent valid file_id returns HTTP 404."""
    non_existent_id = uuid.uuid4().hex
    jd_payload = {
        "file_id": non_existent_id,
        "job_description": "We are looking for a Python Developer with SQL experience.",
    }
    response = client.post("/api/v1/jobs/match", json=jd_payload)
    assert response.status_code == 404
    assert "Resume file" in response.json()["detail"]


# ---------------------------------------------------------------------------
# 12. Corrupt PDF
# ---------------------------------------------------------------------------
def test_corrupt_pdf(mock_upload_env):
    """Verify corrupt PDF returns HTTP 422."""
    file_id = uuid.uuid4().hex
    (mock_upload_env / f"{file_id}.pdf").write_bytes(b"%PDF-1.4 corrupt junk bytes that cannot be opened")

    jd_payload = {
        "file_id": file_id,
        "job_description": "We are looking for a Python Developer with SQL experience.",
    }
    response = client.post("/api/v1/jobs/match", json=jd_payload)
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# 13. Empty or Invalid Job Description
# ---------------------------------------------------------------------------
def test_empty_or_invalid_jd(mock_upload_env):
    """Verify short or empty JD text returns HTTP 422."""
    file_id = uuid.uuid4().hex
    (mock_upload_env / f"{file_id}.pdf").write_bytes(create_realistic_candidate_pdf())

    # Empty JD
    res_empty = client.post("/api/v1/jobs/match", json={"file_id": file_id, "job_description": ""})
    assert res_empty.status_code == 422

    # Too short JD (< 50 chars)
    res_short = client.post("/api/v1/jobs/match", json={"file_id": file_id, "job_description": "Hiring a developer."})
    assert res_short.status_code == 422


# ---------------------------------------------------------------------------
# 14. Oversized Job Description
# ---------------------------------------------------------------------------
def test_oversized_jd(mock_upload_env):
    """Verify JD exceeding 30,000 characters returns HTTP 422."""
    file_id = uuid.uuid4().hex
    (mock_upload_env / f"{file_id}.pdf").write_bytes(create_realistic_candidate_pdf())

    oversized_text = "Software Engineer with Python and SQL experience. " * 700
    assert len(oversized_text) > 30000

    response = client.post("/api/v1/jobs/match", json={"file_id": file_id, "job_description": oversized_text})
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# 15. Missing Candidate Profile / Empty Text PDF
# ---------------------------------------------------------------------------
def test_missing_candidate_profile_empty_pdf(mock_upload_env):
    """Verify PDF with no readable text returns HTTP 422."""
    file_id = uuid.uuid4().hex
    (mock_upload_env / f"{file_id}.pdf").write_bytes(create_empty_text_pdf())

    jd_payload = {
        "file_id": file_id,
        "job_description": "We are looking for a Python Developer with SQL experience.",
    }
    response = client.post("/api/v1/jobs/match", json=jd_payload)
    assert response.status_code == 422
    assert "No readable text" in response.json()["detail"]


# ---------------------------------------------------------------------------
# 16. No Education Requirement (Weight Re-normalization)
# ---------------------------------------------------------------------------
def test_no_education_requirement(mock_upload_env):
    """Verify JD without education requirements re-normalizes weights without unfair penalty."""
    file_id = uuid.uuid4().hex
    (mock_upload_env / f"{file_id}.pdf").write_bytes(create_realistic_candidate_pdf())

    jd_payload = {
        "file_id": file_id,
        "job_description": (
            "Python Backend Engineer.\n"
            "No formal degree required — self-taught developers and bootcamp graduates welcome.\n"
            "Required Skills: Python, SQL, PostgreSQL."
        ),
    }

    response = client.post("/api/v1/jobs/match", json=jd_payload)
    assert response.status_code == 200
    data = response.json()

    edu_comp = data["match_score"]["components"]["education"]
    assert edu_comp["availability"] == "unavailable"
    assert data["match_score"]["weight_normalization_applied"] is True


# ---------------------------------------------------------------------------
# 17. No Experience Requirement
# ---------------------------------------------------------------------------
def test_no_experience_requirement(mock_upload_env):
    """Verify JD without explicit experience requirements defaults safely."""
    file_id = uuid.uuid4().hex
    (mock_upload_env / f"{file_id}.pdf").write_bytes(create_realistic_candidate_pdf())

    jd_payload = {
        "file_id": file_id,
        "job_description": (
            "Junior Software Engineer.\n"
            "Required Skills: Python, SQL, PostgreSQL, Git.\n"
            "Education: Bachelor's in Computer Science."
        ),
    }

    response = client.post("/api/v1/jobs/match", json=jd_payload)
    assert response.status_code == 200
    data = response.json()

    exp = data["experience_match"]
    assert exp is not None
    assert exp["required_years"] is None


# ---------------------------------------------------------------------------
# 18. All Scoring Components Handled Robustly
# ---------------------------------------------------------------------------
def test_all_scoring_components_handled_robustly(mock_upload_env):
    """Verify minimal unstructured JD executes without exceptions."""
    file_id = uuid.uuid4().hex
    (mock_upload_env / f"{file_id}.pdf").write_bytes(create_realistic_candidate_pdf())

    jd_payload = {
        "file_id": file_id,
        "job_description": (
            "General technical team member wanted for high paced startup environment.\n"
            "Seeking smart energetic individuals interested in problem solving and technology."
        ),
    }

    response = client.post("/api/v1/jobs/match", json=jd_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["overall_score"] is not None
    assert 0.0 <= data["overall_score"] <= 100.0


# ---------------------------------------------------------------------------
# 19. No Duplicate Skill Evidence
# ---------------------------------------------------------------------------
def test_no_duplicate_skill_evidence(mock_upload_env):
    """Verify skills repeated across JD sentences are deduplicated in matching results."""
    file_id = uuid.uuid4().hex
    (mock_upload_env / f"{file_id}.pdf").write_bytes(create_realistic_candidate_pdf())

    jd_payload = {
        "file_id": file_id,
        "job_description": (
            "Python Engineer needed.\n"
            "We love Python developers.\n"
            "Python is required for our backend services.\n"
            "Strong knowledge of Python and SQL is mandatory."
        ),
    }

    response = client.post("/api/v1/jobs/match", json=jd_payload)
    assert response.status_code == 200
    data = response.json()

    python_items = [item for item in data["matched_skills"] if item["skill"] == "Python"]
    assert len(python_items) == 1


# ---------------------------------------------------------------------------
# 20. Response Schema Validation
# ---------------------------------------------------------------------------
def test_response_schema_validation(mock_upload_env):
    """Verify entire JSON response passes strict Pydantic model validation."""
    file_id = uuid.uuid4().hex
    (mock_upload_env / f"{file_id}.pdf").write_bytes(create_realistic_candidate_pdf())

    jd_payload = {
        "file_id": file_id,
        "job_title": "Full Stack Engineer",
        "company": "TechInnovate",
        "location": "Hybrid",
        "job_description": (
            "Full Stack Engineer.\n"
            "Requirements:\n"
            "- Python, SQL, PostgreSQL.\n"
            "- 2+ years of experience.\n"
            "- Bachelor's in Computer Science.\n"
            "Preferred: AWS, Docker."
        ),
    }

    response = client.post("/api/v1/jobs/match", json=jd_payload)
    assert response.status_code == 200

    parsed_response = JobMatchResponse.model_validate(response.json())
    assert parsed_response.success is True
    assert parsed_response.file_id == file_id
    assert parsed_response.parsed_job.job_title == "Full Stack Engineer"


# ---------------------------------------------------------------------------
# 21. Candidate Privacy Protection (Zero PII Leaks)
# ---------------------------------------------------------------------------
def test_candidate_privacy_no_pii_exposed(mock_upload_env):
    """Verify response never exposes candidate phone, email, full text, or personal address."""
    file_id = uuid.uuid4().hex
    (mock_upload_env / f"{file_id}.pdf").write_bytes(create_realistic_candidate_pdf())

    jd_payload = {
        "file_id": file_id,
        "job_description": "We are seeking a Python developer with SQL and PostgreSQL knowledge.",
    }

    response = client.post("/api/v1/jobs/match", json=jd_payload)
    assert response.status_code == 200
    data = response.json()

    # Summary must omit personal identifiers
    assert "name" not in data["candidate_summary"]
    assert "email" not in data["candidate_summary"]
    assert "phone" not in data["candidate_summary"]
    assert "location" not in data["candidate_summary"]

    # String serialized response must never leak candidate raw contact details
    response_str = response.text
    assert "edu.shivam0903@gmail.com" not in response_str
    assert "8887602317" not in response_str
    assert "full_text" not in data


# ---------------------------------------------------------------------------
# 22. All Scoring Components Unavailable Integration
# ---------------------------------------------------------------------------
def test_all_scoring_components_unavailable_integration(mock_upload_env, monkeypatch):
    """Verify that when all components are unavailable, classification is 'Not assessable' and score is None."""
    from matching_engine import score_calculator
    from schemas.matching_schema import ComponentAvailability, ComponentScore, MatchScoreBreakdown

    file_id = uuid.uuid4().hex
    (mock_upload_env / f"{file_id}.pdf").write_bytes(create_realistic_candidate_pdf())

    def mock_calc_score(*args, **kwargs):
        comps = {
            cname: ComponentScore(
                component_name=cname,
                availability=ComponentAvailability.UNAVAILABLE,
                raw_score=None,
                base_weight=0.2,
                normalized_weight=0.0,
                weighted_contribution=0.0,
                evidence=[],
                reason="Unassessed",
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

    monkeypatch.setattr(score_calculator, "calculate_match_score", mock_calc_score)
    # Also monkeypatch matching_service's imported calculate_match_score
    from matching_engine import matching_service
    monkeypatch.setattr(matching_service, "calculate_match_score", mock_calc_score)

    jd_payload = {
        "file_id": file_id,
        "job_description": "We are seeking a Python developer with SQL and PostgreSQL knowledge.",
    }

    response = client.post("/api/v1/jobs/match", json=jd_payload)
    assert response.status_code == 200
    data = response.json()

    # 1. Root and match_score fields support None / Not assessable
    assert data["overall_score"] is None
    assert data["match_classification"] == "Not assessable"
    assert data["match_score"]["overall_score"] is None
    assert data["match_score"]["match_classification"] == "Not assessable"
    assert data["match_classification"] != "Low Match"

    # 2. Complete Pydantic schema validation using actual JobMatchResponse model
    validated_model = JobMatchResponse.model_validate(data)
    assert validated_model.overall_score is None
    assert validated_model.match_classification == "Not assessable"
    assert validated_model.match_score is not None
    assert validated_model.match_score.overall_score is None
    assert validated_model.match_score.match_classification == "Not assessable"

    # 3. Verify JSON serialization produces null and "Not assessable"
    serialized_json = validated_model.model_dump_json()
    assert '"overall_score":null' in serialized_json.replace(" ", "")
    assert '"match_classification":"Not assessable"' in serialized_json

    # 4. Verify FastAPI HTTP serialized response payload
    raw_response_text = response.text.replace(" ", "")
    assert '"overall_score":null' in raw_response_text
    assert '"match_classification":"Not assessable"' in response.text


# ---------------------------------------------------------------------------
# 23. Partially Available Components Weight Normalization
# ---------------------------------------------------------------------------
def test_partially_available_components_normalize_weights(mock_upload_env):
    """Verify that when some components are unavailable, available weights sum to 1.0."""
    file_id = uuid.uuid4().hex
    (mock_upload_env / f"{file_id}.pdf").write_bytes(create_realistic_candidate_pdf())

    # JD with no education requirement ("no degree required")
    jd_payload = {
        "file_id": file_id,
        "job_description": (
            "Backend Python Developer.\n"
            "Requirements:\n"
            "- Python and SQL required.\n"
            "- 2+ years of experience.\n"
            "No formal degree or college education required."
        ),
    }

    response = client.post("/api/v1/jobs/match", json=jd_payload)
    assert response.status_code == 200
    data = response.json()

    score_data = data["match_score"]
    assert score_data["weight_normalization_applied"] is True

    # Unavailable component has 0.0 normalized weight
    edu_comp = score_data["components"]["education"]
    assert edu_comp["availability"] == "unavailable"
    assert edu_comp["normalized_weight"] == 0.0
    assert edu_comp["weighted_contribution"] == 0.0

    # Sum of available normalized weights equals 1.0
    available_norm_weights = [
        c["normalized_weight"]
        for c in score_data["components"].values()
        if c["availability"] == "available"
    ]
    assert pytest.approx(sum(available_norm_weights), abs=1e-3) == 1.0


# ---------------------------------------------------------------------------
# 24. Recommendation Safety (No Blind Resume Claims)
# ---------------------------------------------------------------------------
def test_recommendation_safety_requires_evidence_before_resume_update(mock_upload_env):
    """Verify recommendations advise building practical projects before adding related/missing skills."""
    file_id = uuid.uuid4().hex
    (mock_upload_env / f"{file_id}.pdf").write_bytes(create_realistic_candidate_pdf())

    jd_payload = {
        "file_id": file_id,
        "job_description": (
            "Senior Backend Engineer.\n"
            "Required Skills:\n"
            "- FastAPI framework development.\n"
            "- Kubernetes container orchestration.\n"
        ),
    }

    response = client.post("/api/v1/jobs/match", json=jd_payload)
    assert response.status_code == 200
    data = response.json()

    for rec in data["recommendations"]:
        if rec["category"] in ("required_skill", "related_skill"):
            # Must recommend learning/project first and not advise blindly claiming unevidenced skills
            assert any(
                "Only after" in act or "deliverables" in act or "working" in act or "project" in act.lower()
                for act in rec["suggested_actions"]
            )
