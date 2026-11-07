"""
Unit tests for Job Description Parsing Engine and Schemas (Phase 5.1).

Tests:
- Job description validation (empty, short, meaningless, oversized)
- Section segmentation (Required, Preferred, Responsibilities, Overview)
- Job title, company, and location resolution (explicit vs extracted)
- Required and Preferred skill extraction with verbatim evidence
- Priority of required skills over preferred (deduplication)
- Duplicate overlap suppression (Data Structures & Algorithms)
- Experience requirements (years, ranges, seniority level, evidence)
- Education requirements (degrees, disciplines, required vs preferred)
- Responsibilities and domain keywords
- Pydantic schema validation (JobDescriptionRequest, ComponentScore availability)
"""

import pytest
from matching_engine.jd_parser import parse_job_description
from schemas.matching_schema import (
    JobDescriptionRequest,
    ComponentAvailability,
    ComponentScore,
    ParsedJobDescription,
)


SAMPLE_STANDARD_JD = """
Job Title: Senior Full-Stack Engineer
Company: CloudScale Technologies
Location: Remote

About the Role:
CloudScale is looking for an experienced Senior Full-Stack Engineer to lead the design and development of our next-generation cloud analytics platform.

Responsibilities:
• Architect, build, and maintain scalable web applications and microservices.
• Collaborate with cross-functional teams to design RESTful APIs and real-time streaming services.
• Mentor junior engineers and participate in architecture and code reviews.
• Optimize application performance and ensure high availability.

Required Qualifications:
• 5+ years of software engineering experience building production systems.
• Bachelor's degree in Computer Science or Software Engineering.
• Strong proficiency in Python, JavaScript, and TypeScript.
• Hands-on experience with React, Node.js, and FastAPI.
• Solid background in PostgreSQL and MongoDB database design.
• Proven track record with Docker, Kubernetes, and AWS cloud services.
• Deep understanding of Data Structures & Algorithms, System Design, and CI/CD pipelines.

Preferred Qualifications:
• Master's degree in Computer Science or related quantitative field.
• Experience with Next.js, Redis caching, and GraphQL.
• Familiarity with PyTorch or machine learning workflows is a plus.
• Contributions to open-source software.
"""


def test_parse_standard_job_description_success():
    """Verify comprehensive parsing of a realistic multi-section job description."""
    parsed = parse_job_description(SAMPLE_STANDARD_JD)

    assert isinstance(parsed, ParsedJobDescription)
    assert parsed.job_title == "Senior Full-Stack Engineer"
    assert parsed.company == "CloudScale Technologies"
    assert parsed.location == "Remote"

    # Required Skills
    assert "Python" in parsed.required_skills
    assert "TypeScript" in parsed.required_skills
    assert "React" in parsed.required_skills
    assert "FastAPI" in parsed.required_skills
    assert "Node.js" in parsed.required_skills
    assert "PostgreSQL" in parsed.required_skills
    assert "Docker" in parsed.required_skills
    assert "Kubernetes" in parsed.required_skills
    assert "AWS" in parsed.required_skills
    assert "Data Structures & Algorithms" in parsed.required_skills

    # Overlap suppression: DSA must not be duplicated
    assert "DSA" not in parsed.required_skills
    assert "Algorithms" not in parsed.required_skills

    # Preferred Skills
    assert "Next.js" in parsed.preferred_skills
    assert "Redis" in parsed.preferred_skills
    assert "GraphQL" in parsed.preferred_skills
    assert "PyTorch" in parsed.preferred_skills

    # No duplicate skill between Required and Preferred (Required takes strict precedence)
    for req in parsed.required_skills:
        assert req not in parsed.preferred_skills

    # Skill Evidence verification
    assert "Python" in parsed.skill_evidence
    assert "TypeScript" in parsed.skill_evidence["Python"] or "Python" in parsed.skill_evidence["Python"]

    # Experience Requirements
    exp = parsed.experience_requirement
    assert exp.minimum_years == 5.0
    assert exp.level == "Senior"
    assert exp.is_required is True
    assert "5+" in exp.evidence

    # Education Requirements
    edu = parsed.education_requirement
    assert edu.required_degree == "Bachelor"
    assert "Computer Science" in edu.fields_of_study
    assert edu.is_required is True
    assert "Bachelor" in edu.evidence

    # Responsibilities & Keywords
    assert len(parsed.responsibilities) >= 3
    assert any("microservices" in r.lower() for r in parsed.responsibilities)
    assert "Microservices" in parsed.keywords
    assert "System Design" in parsed.keywords


def test_explicit_arguments_override_jd_text():
    """Verify that explicitly supplied title, company, and location take priority."""
    parsed = parse_job_description(
        SAMPLE_STANDARD_JD,
        job_title="Lead Platform Architect",
        company="Custom Corp",
        location="New York, NY",
    )
    assert parsed.job_title == "Lead Platform Architect"
    assert parsed.company == "Custom Corp"
    assert parsed.location == "New York, NY"


def test_experience_range_parsing():
    """Verify extraction of experience range (e.g. 3-5 years)."""
    jd_text = """
    Software Developer Position
    We are seeking a developer with 3 to 5 years of relevant software engineering experience.
    Must have solid knowledge of Java and Spring Boot.
    Bachelor's degree required.
    """
    parsed = parse_job_description(jd_text)
    assert parsed.experience_requirement.minimum_years == 3.0
    assert parsed.experience_requirement.maximum_years == 5.0
    assert parsed.experience_requirement.is_required is True


def test_entry_level_no_years_experience():
    """Verify detection of Entry-level / Junior roles without explicit years."""
    jd_text = """
    Associate Software Engineer
    Company: Tech Innovators
    We are hiring an Entry-level Software Engineer to join our frontend engineering team.
    Requirements:
    • Bachelor's degree in Computer Science or IT.
    • Solid understanding of HTML5, CSS3, and JavaScript.
    • Experience with React or Vue.js is a plus.
    """
    parsed = parse_job_description(jd_text)
    assert parsed.experience_requirement.minimum_years is None
    assert parsed.experience_requirement.level == "Entry-level"
    assert "React" in parsed.preferred_skills or "React" in parsed.required_skills
    assert "JavaScript" in parsed.required_skills


def test_no_education_requirement_specified():
    """Verify that when no degree is mentioned, education requirement is cleanly marked unrequired."""
    jd_text = """
    Full Stack Developer
    We care about your skills and code, not where you went to school.
    Must have 2+ years of hands-on experience with Python, Django, and PostgreSQL.
    Demonstrated ability to build web applications.
    """
    parsed = parse_job_description(jd_text)
    assert parsed.education_requirement.required_degree is None
    assert parsed.education_requirement.fields_of_study == []
    assert parsed.education_requirement.is_required is False
    assert parsed.education_requirement.evidence is None


def test_unstructured_jd_without_headings():
    """Verify extraction from freeform text without standard headings."""
    jd_text = """
    Looking for a Python Developer in London with at least 3 years experience.
    The candidate must have strong knowledge of FastAPI, Docker, and PostgreSQL.
    Knowledge of Kubernetes and AWS is preferred.
    Bachelor's in Computer Science preferred.
    """
    parsed = parse_job_description(jd_text)
    assert "Python" in parsed.required_skills
    assert "FastAPI" in parsed.required_skills
    assert "Docker" in parsed.required_skills
    assert "PostgreSQL" in parsed.required_skills
    assert "Kubernetes" in parsed.preferred_skills
    assert "AWS" in parsed.preferred_skills
    assert parsed.experience_requirement.minimum_years == 3.0
    assert parsed.education_requirement.required_degree == "Bachelor"
    assert parsed.education_requirement.is_required is False  # Explicitly preferred in JD text


def test_qa_regression_testing_does_not_trigger_ml_regression():
    """Ensure that QA testing phrasing does not falsely add Machine Learning Regression to JD skills."""
    jd_text = """
    QA Automation Engineer
    Requirements:
    • 3+ years experience in automated testing.
    • Performed functional and regression testing across web applications.
    • Hands-on experience with Python, Selenium, Postman, and Git.
    """
    parsed = parse_job_description(jd_text)
    assert "Regression" not in parsed.required_skills
    assert "Regression" not in parsed.preferred_skills
    assert "Python" in parsed.required_skills
    assert "Postman" in parsed.required_skills


# ============================================================================
# Validation & Error Handling Tests
# ============================================================================

def test_parse_empty_string_raises_value_error():
    """Verify that empty JD text raises a descriptive ValueError."""
    with pytest.raises(ValueError, match="cannot be empty"):
        parse_job_description("")


def test_parse_whitespace_raises_value_error():
    """Verify that whitespace-only text raises a ValueError."""
    with pytest.raises(ValueError, match="cannot be empty"):
        parse_job_description("   \n\t   ")


def test_parse_too_short_text_raises_value_error():
    """Verify that text under 50 characters raises ValueError."""
    with pytest.raises(ValueError, match="too short"):
        parse_job_description("Software Developer needed immediately.")


def test_parse_meaningless_words_raises_value_error():
    """Verify that non-word characters under min words threshold raise ValueError."""
    with pytest.raises(ValueError, match="not contain enough recognizable words"):
        parse_job_description("....................................................................")


def test_parse_oversized_text_raises_value_error():
    """Verify that text exceeding 30,000 characters is rejected."""
    oversized = "Job requirement: Python developer. " * 1000  # ~35,000 chars
    with pytest.raises(ValueError, match="exceeds maximum allowed length"):
        parse_job_description(oversized)


# ============================================================================
# Pydantic Schema Validation Tests
# ============================================================================

def test_job_description_request_schema_valid():
    """Verify JobDescriptionRequest validates valid payloads properly."""
    req = JobDescriptionRequest(
        job_description=SAMPLE_STANDARD_JD,
        job_title="Senior Engineer",
        company="Acme Corp",
        location="Remote",
        file_id="1731d6216e504422b0667e3f00c0f9e2",
    )
    assert req.job_title == "Senior Engineer"
    assert req.company == "Acme Corp"
    assert req.file_id == "1731d6216e504422b0667e3f00c0f9e2"
    assert len(req.job_description) > 50


def test_job_description_request_schema_rejects_empty():
    """Verify schema raises validation error on empty string."""
    with pytest.raises(Exception):
        JobDescriptionRequest(job_description="")


def test_job_description_request_schema_rejects_too_short():
    """Verify schema raises validation error on short text."""
    with pytest.raises(Exception):
        JobDescriptionRequest(job_description="Hiring a developer.")


def test_component_score_availability_model():
    """Verify ComponentScore handles available, unavailable, and insufficient data explicitly."""
    available_score = ComponentScore(
        component_name="required_skills",
        availability=ComponentAvailability.AVAILABLE,
        raw_score=85.0,
        base_weight=0.40,
        normalized_weight=0.40,
        weighted_contribution=34.0,
        evidence=["Matched Python, React, and FastAPI"],
    )
    assert available_score.availability == "available"
    assert available_score.raw_score == 85.0

    unavailable_score = ComponentScore(
        component_name="education",
        availability=ComponentAvailability.UNAVAILABLE,
        raw_score=None,
        base_weight=0.10,
        normalized_weight=0.0,
        weighted_contribution=0.0,
        evidence=[],
        reason="Target job description has no explicit degree requirement.",
    )
    assert unavailable_score.availability == "unavailable"
    assert unavailable_score.raw_score is None
    assert unavailable_score.weighted_contribution == 0.0

