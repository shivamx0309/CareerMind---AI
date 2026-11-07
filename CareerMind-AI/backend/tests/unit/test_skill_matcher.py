"""
Unit tests for Skill Normalization and Matching Engine (Phase 5.2).

Tests:
- Exact matches (case-insensitive)
- Canonical alias matches (e.g. React.js -> React)
- Related but non-exact skills (semantically_related with 0.6 confidence)
- Missing skills with no evidence (confidence 0.0)
- Evidence from technical_skills, experience, projects, certifications, and achievements
- Prevention of double-counting across multiple evidence sources
- Protection against false positive prose (regression testing != ML Regression)
- Empty candidate profile handling
"""

import pytest
from schemas.candidate_schema import (
    CandidateProfile,
    TechnicalSkills,
    ExperienceEntry,
    ProjectEntry,
    CertificationEntry,
    AchievementEntry,
)
from schemas.matching_schema import (
    ParsedJobDescription,
    SkillMatchStatus,
    SkillRequirementType,
    ExperienceRequirement,
    EducationRequirement,
)
from matching_engine.skill_matcher import (
    match_candidate_skills,
    extract_candidate_skill_evidence,
)


def _build_dummy_parsed_jd(
    required_skills: list[str],
    preferred_skills: list[str] | None = None,
    evidence: dict[str, str] | None = None,
) -> ParsedJobDescription:
    """Helper to construct a ParsedJobDescription fixture."""
    return ParsedJobDescription(
        raw_text="Sample JD text",
        job_title="Software Engineer",
        required_skills=required_skills,
        preferred_skills=preferred_skills or [],
        skill_evidence=evidence or {},
        experience_requirement=ExperienceRequirement(),
        education_requirement=EducationRequirement(),
        responsibilities=[],
        keywords=[],
    )


def test_exact_match_case_insensitive():
    """Verify exact match when candidate has canonical skill name with differing case."""
    candidate = CandidateProfile(
        technical_skills=TechnicalSkills(
            programming_languages=["Python", "SQL"],
            backend=["FastAPI"],
        )
    )
    jd = _build_dummy_parsed_jd(required_skills=["python", "FastAPI"])

    items, missing_req, _ = match_candidate_skills(candidate, jd)

    assert len(items) == 2
    assert missing_req == []

    python_item = next(i for i in items if i.skill == "Python")
    assert python_item.status == SkillMatchStatus.EXACT_MATCH
    assert python_item.match_confidence == 1.0
    assert python_item.evidence_source == "technical_skills"

    fastapi_item = next(i for i in items if i.skill == "FastAPI")
    assert fastapi_item.status == SkillMatchStatus.EXACT_MATCH
    assert fastapi_item.match_confidence == 1.0


def test_canonical_alias_match():
    """Verify alias match when candidate uses React.js or REST APIs and JD specifies canonical name."""
    candidate = CandidateProfile(
        technical_skills=TechnicalSkills(
            frontend=["React.js"],
            backend=["REST APIs"],
            databases=["Postgres"],
        )
    )
    jd = _build_dummy_parsed_jd(required_skills=["React", "REST API", "PostgreSQL"])

    items, missing_req, _ = match_candidate_skills(candidate, jd)

    assert len(items) == 3
    assert missing_req == []

    react_item = next(i for i in items if i.skill == "React")
    assert react_item.status == SkillMatchStatus.ALIAS_MATCH
    assert react_item.candidate_evidence == "React.js"
    assert react_item.match_confidence == 1.0

    rest_item = next(i for i in items if i.skill == "REST API")
    assert rest_item.status == SkillMatchStatus.ALIAS_MATCH
    assert rest_item.candidate_evidence == "REST APIs"

    pg_item = next(i for i in items if i.skill == "PostgreSQL")
    assert pg_item.status == SkillMatchStatus.ALIAS_MATCH
    assert pg_item.candidate_evidence == "Postgres"


def test_missing_skill_no_evidence():
    """Verify missing skill classification when candidate has no evidence whatsoever."""
    candidate = CandidateProfile(
        technical_skills=TechnicalSkills(
            programming_languages=["Python"],
            backend=["FastAPI"],
        )
    )
    jd = _build_dummy_parsed_jd(
        required_skills=["Python", "Docker", "Kubernetes"],
        preferred_skills=["AWS"],
    )

    items, missing_req, missing_pref = match_candidate_skills(candidate, jd)

    assert "Docker" in missing_req
    assert "Kubernetes" in missing_req
    assert "AWS" in missing_pref

    docker_item = next(i for i in items if i.skill == "Docker")
    assert docker_item.status == SkillMatchStatus.MISSING
    assert docker_item.match_confidence == 0.0
    assert docker_item.candidate_evidence is None
    assert docker_item.evidence_source is None


def test_semantically_related_skill_not_exact():
    """Verify related skill detection (e.g. candidate has Django, JD asks for FastAPI)."""
    candidate = CandidateProfile(
        technical_skills=TechnicalSkills(
            programming_languages=["Python"],
            backend=["Django"],  # Same cluster: Python Web Frameworks
            databases=["MySQL"],  # Same cluster: Relational SQL Databases
        )
    )
    jd = _build_dummy_parsed_jd(
        required_skills=["FastAPI", "PostgreSQL", "Docker"]
    )

    items, missing_req, _ = match_candidate_skills(candidate, jd)

    # FastAPI related through Django
    fastapi_item = next(i for i in items if i.skill == "FastAPI")
    assert fastapi_item.status == SkillMatchStatus.SEMANTICALLY_RELATED
    assert fastapi_item.match_confidence == 0.6
    assert "Django" in fastapi_item.candidate_evidence
    assert "Python Web Frameworks" in fastapi_item.candidate_evidence
    # Not counted as exact match!
    assert fastapi_item.status != SkillMatchStatus.EXACT_MATCH

    # PostgreSQL related through MySQL
    pg_item = next(i for i in items if i.skill == "PostgreSQL")
    assert pg_item.status == SkillMatchStatus.SEMANTICALLY_RELATED
    assert pg_item.match_confidence == 0.6
    assert "MySQL" in pg_item.candidate_evidence

    # Docker has no related cluster match -> strictly missing
    docker_item = next(i for i in items if i.skill == "Docker")
    assert docker_item.status == SkillMatchStatus.MISSING


def test_evidence_from_experience():
    """Verify skill extracted from work experience description when not in technical_skills."""
    candidate = CandidateProfile(
        technical_skills=TechnicalSkills(
            programming_languages=["JavaScript"],
        ),
        experience=[
            ExperienceEntry(
                job_title="Software Developer",
                company="Tech Solutions",
                description="• Built scalable backend services using Node.js and Express.",
                technologies=["PostgreSQL"],
            )
        ],
    )
    jd = _build_dummy_parsed_jd(required_skills=["Node.js", "Express", "PostgreSQL"])

    items, missing_req, _ = match_candidate_skills(candidate, jd)

    assert missing_req == []

    node_item = next(i for i in items if i.skill == "Node.js")
    assert node_item.status == SkillMatchStatus.EXACT_MATCH
    assert "experience" in node_item.evidence_source

    pg_item = next(i for i in items if i.skill == "PostgreSQL")
    assert pg_item.status == SkillMatchStatus.EXACT_MATCH
    assert "experience" in pg_item.evidence_source


def test_evidence_from_projects():
    """Verify skill matched from project technologies and description."""
    candidate = CandidateProfile(
        technical_skills=TechnicalSkills(),
        projects=[
            ProjectEntry(
                project_name="E-Commerce API",
                technologies=["MongoDB", "Redis", "Socket.IO"],
                description="Built full-stack real-time store with Socket.IO messaging.",
            )
        ],
    )
    jd = _build_dummy_parsed_jd(required_skills=["MongoDB", "Redis", "Socket.IO"])

    items, missing_req, _ = match_candidate_skills(candidate, jd)

    assert missing_req == []
    for item in items:
        assert item.status == SkillMatchStatus.EXACT_MATCH
        assert "projects" in item.evidence_source


def test_evidence_from_certifications():
    """Verify skill matched from certifications."""
    candidate = CandidateProfile(
        technical_skills=TechnicalSkills(),
        certifications=[
            CertificationEntry(
                certification_name="AWS Certified Solutions Architect",
                issuing_organization="Amazon Web Services",
            )
        ],
    )
    jd = _build_dummy_parsed_jd(required_skills=["AWS"])

    items, missing_req, _ = match_candidate_skills(candidate, jd)

    assert missing_req == []
    aws_item = items[0]
    assert aws_item.skill == "AWS"
    assert aws_item.status == SkillMatchStatus.EXACT_MATCH
    assert "certifications" in aws_item.evidence_source


def test_no_double_counting_across_multiple_sources():
    """Verify that a skill found in technical_skills, experience, and projects is evaluated exactly once."""
    candidate = CandidateProfile(
        technical_skills=TechnicalSkills(
            frontend=["React"],
        ),
        experience=[
            ExperienceEntry(
                job_title="Frontend Developer",
                company="Company A",
                technologies=["React"],
                description="• Built React UI.",
            )
        ],
        projects=[
            ProjectEntry(
                project_name="Web App",
                technologies=["React"],
            )
        ],
    )
    jd = _build_dummy_parsed_jd(required_skills=["React"])

    items, missing_req, _ = match_candidate_skills(candidate, jd)

    # Exactly 1 item for React
    react_items = [i for i in items if i.skill == "React"]
    assert len(react_items) == 1
    # Multiple sources consolidated
    assert "technical_skills" in react_items[0].evidence_source
    assert "experience" in react_items[0].evidence_source
    assert "projects" in react_items[0].evidence_source


def test_regression_testing_does_not_match_ml_regression():
    """Verify that QA 'regression testing' does not match Machine Learning 'Regression' requirement."""
    candidate = CandidateProfile(
        experience=[
            ExperienceEntry(
                job_title="QA Tester",
                company="QA Corp",
                description="Performed functional and regression testing across UI components.",
            )
        ]
    )
    jd = _build_dummy_parsed_jd(required_skills=["Regression"])

    items, missing_req, _ = match_candidate_skills(candidate, jd)

    assert "Regression" in missing_req
    reg_item = items[0]
    assert reg_item.status == SkillMatchStatus.MISSING


def test_java_does_not_match_javascript():
    """Verify that Java and JavaScript are strictly separated and do not cross-match."""
    candidate = CandidateProfile(
        technical_skills=TechnicalSkills(
            programming_languages=["Java"],
        )
    )
    jd = _build_dummy_parsed_jd(required_skills=["JavaScript"])

    items, missing_req, _ = match_candidate_skills(candidate, jd)

    assert "JavaScript" in missing_req
    js_item = items[0]
    assert js_item.status == SkillMatchStatus.MISSING


def test_empty_candidate_profile():
    """Verify that an empty candidate profile marks all JD skills as missing without crashing."""
    candidate = CandidateProfile()
    jd = _build_dummy_parsed_jd(
        required_skills=["Python", "FastAPI", "Docker"],
        preferred_skills=["AWS", "Redis"],
    )

    items, missing_req, missing_pref = match_candidate_skills(candidate, jd)

    assert len(items) == 5
    assert len(missing_req) == 3
    assert len(missing_pref) == 2
    for item in items:
        assert item.status == SkillMatchStatus.MISSING
        assert item.match_confidence == 0.0

