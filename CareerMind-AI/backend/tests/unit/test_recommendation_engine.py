"""
Unit tests for Actionable Recommendation Engine (Phase 5.5).

Verifies:
- Missing required skill recommendation (HIGH priority)
- Missing preferred skill recommendation (LOW priority)
- Related skill bridge recommendation (MEDIUM priority)
- Already matched skills produce NO recommendation
- Professional experience tenure gap
- Internship vs professional experience distinction
- Project-building recommendation when project count is 0
- Missing mandatory education (HIGH priority, legitimate pathways)
- Preferred education gap (LOW priority)
- Duplicate recommendation suppression
- Priority ordering (HIGH -> MEDIUM -> LOW)
- Evidence preservation
- Empty recommendation result for perfect match
- Graceful handling of missing/insufficient data
"""

import pytest

from schemas.matching_schema import (
    ParsedJobDescription,
    SkillMatchItem,
    SkillMatchStatus,
    SkillRequirementType,
    ExperienceMatchResult,
    ExperienceAssessmentStatus,
    ExperienceRequirement,
    EducationMatchResult,
    EducationMatchStatus,
    EducationRequirement,
    RecommendationPriority,
    RecommendationCategory,
    ActionableRecommendation,
)
from matching_engine.recommendation_engine import generate_recommendations


@pytest.fixture
def base_parsed_jd():
    """Minimal parsed JD for recommendation tests."""
    return ParsedJobDescription(
        raw_text="Software Engineer with Python, Docker and AWS experience required.",
        job_title="Software Engineer",
        required_skills=["Python", "Docker", "AWS"],
        preferred_skills=["Redis"],
        responsibilities=["Design and maintain backend microservices."],
        experience_requirement=ExperienceRequirement(minimum_years=3.0),
        education_requirement=EducationRequirement(
            required_degree="Bachelor's",
            required_fields=["Computer Science"],
            is_required=True,
        ),
    )


def test_missing_required_skill_recommendation(base_parsed_jd):
    """Missing required skill generates HIGH priority recommendation with practical action steps."""
    matched_skills = [
        SkillMatchItem(
            skill="Docker",
            requirement_type=SkillRequirementType.REQUIRED,
            status=SkillMatchStatus.MISSING,
            original_jd_phrase="Docker experience required.",
        ),
    ]

    recs = generate_recommendations(
        parsed_jd=base_parsed_jd,
        matched_skills=matched_skills,
    )

    assert len(recs) == 1
    rec = recs[0]
    assert rec.priority == RecommendationPriority.HIGH
    assert rec.category == RecommendationCategory.REQUIRED_SKILL
    assert rec.related_requirement == "Docker"
    assert rec.candidate_evidence is None
    assert rec.source_component == "skill"
    assert len(rec.suggested_actions) >= 2
    assert any("Docker" in action for action in rec.suggested_actions)
    assert rec.estimated_effort == "2-4 weeks"


def test_missing_preferred_skill_recommendation(base_parsed_jd):
    """Missing preferred skill generates LOW priority recommendation."""
    matched_skills = [
        SkillMatchItem(
            skill="Redis",
            requirement_type=SkillRequirementType.PREFERRED,
            status=SkillMatchStatus.MISSING,
            original_jd_phrase="Redis preferred.",
        ),
    ]

    recs = generate_recommendations(
        parsed_jd=base_parsed_jd,
        matched_skills=matched_skills,
    )

    assert len(recs) == 1
    rec = recs[0]
    assert rec.priority == RecommendationPriority.LOW
    assert rec.category == RecommendationCategory.PREFERRED_SKILL
    assert rec.related_requirement == "Redis"
    assert "preferred" in rec.description.lower()
    assert rec.estimated_effort == "1-2 weeks"


def test_related_skill_recommendation(base_parsed_jd):
    """Semantically related skill generates MEDIUM priority bridging recommendation."""
    matched_skills = [
        SkillMatchItem(
            skill="FastAPI",
            requirement_type=SkillRequirementType.REQUIRED,
            status=SkillMatchStatus.SEMANTICALLY_RELATED,
            candidate_evidence="Django",
            match_confidence=0.6,
        ),
    ]

    recs = generate_recommendations(
        parsed_jd=base_parsed_jd,
        matched_skills=matched_skills,
    )

    assert len(recs) == 1
    rec = recs[0]
    assert rec.priority == RecommendationPriority.MEDIUM
    assert rec.category == RecommendationCategory.RELATED_SKILL
    assert rec.related_requirement == "FastAPI"
    assert rec.candidate_evidence == "Django"
    assert "Django" in rec.description
    assert "FastAPI" in rec.description
    assert rec.estimated_effort == "1-2 weeks"


def test_already_matched_skill_produces_no_recommendation(base_parsed_jd):
    """Exact match or canonical alias match produces NO recommendation."""
    matched_skills = [
        SkillMatchItem(
            skill="Python",
            requirement_type=SkillRequirementType.REQUIRED,
            status=SkillMatchStatus.EXACT_MATCH,
            candidate_evidence="Python",
            match_confidence=1.0,
        ),
        SkillMatchItem(
            skill="PostgreSQL",
            requirement_type=SkillRequirementType.REQUIRED,
            status=SkillMatchStatus.ALIAS_MATCH,
            candidate_evidence="Postgres",
            match_confidence=1.0,
        ),
    ]

    recs = generate_recommendations(
        parsed_jd=base_parsed_jd,
        matched_skills=matched_skills,
    )

    assert len(recs) == 0


def test_experience_gap_recommendation(base_parsed_jd):
    """Candidate with insufficient professional tenure receives an experience gap recommendation."""
    exp_match = ExperienceMatchResult(
        assessment=ExperienceAssessmentStatus.BELOW_REQUIREMENT,
        required_years=4.0,
        professional_years=1.0,
        internship_years=0.0,
        project_evidence=[{"title": "P1"}, {"title": "P2"}],
        relevant_responsibilities=["Backend microservices"],
        explanation="Candidate has 1.0 years, required 4.0 years.",
    )

    recs = generate_recommendations(
        parsed_jd=base_parsed_jd,
        matched_skills=[],
        experience_match=exp_match,
    )

    assert len(recs) == 1
    rec = recs[0]
    assert rec.category == RecommendationCategory.EXPERIENCE
    assert rec.priority == RecommendationPriority.HIGH  # Gap is 3.0 >= 2.0
    assert rec.source_component == "experience"
    assert "1.0 yrs vs 4.0 yrs" in rec.title
    assert any("portfolio" in action.lower() or "production" in action.lower() for action in rec.suggested_actions)


def test_internship_vs_professional_experience_distinction(base_parsed_jd):
    """Distinguishes internship experience from commercial employment without false merging."""
    exp_match = ExperienceMatchResult(
        assessment=ExperienceAssessmentStatus.PARTIAL,
        required_years=3.0,
        professional_years=1.0,
        internship_years=1.5,
        project_evidence=[{"title": "P1"}],
        relevant_responsibilities=["Backend microservices"],
        explanation="1.0 years professional, 1.5 years internship.",
    )

    recs = generate_recommendations(
        parsed_jd=base_parsed_jd,
        matched_skills=[],
        experience_match=exp_match,
    )

    assert len(recs) == 1
    rec = recs[0]
    assert rec.category == RecommendationCategory.EXPERIENCE
    # Check that description explicitly mentions both professional and internship tenures
    assert "1.0 years of full-time professional" in rec.description
    assert "1.5 years of internship" in rec.description
    assert "1.0 yrs professional, 1.5 yrs internship" in rec.candidate_evidence


def test_project_building_recommendation(base_parsed_jd):
    """Candidate with zero projects receives a dedicated project recommendation."""
    exp_match = ExperienceMatchResult(
        assessment=ExperienceAssessmentStatus.MEETS_REQUIREMENT,
        required_years=2.0,
        professional_years=2.0,
        internship_years=0.0,
        project_evidence=[],
        relevant_responsibilities=["Backend microservices"],
        explanation="2.0 years professional, 0 projects.",
    )

    recs = generate_recommendations(
        parsed_jd=base_parsed_jd,
        matched_skills=[],
        experience_match=exp_match,
    )

    assert len(recs) == 1
    rec = recs[0]
    assert rec.category == RecommendationCategory.PROJECT
    assert "Build and Document Production-Grade Portfolio Projects" in rec.title
    assert any("GitHub" in action for action in rec.suggested_actions)


def test_missing_mandatory_education(base_parsed_jd):
    """Missing mandatory degree produces HIGH priority recommendation with legitimate pathways."""
    edu_match = EducationMatchResult(
        status=EducationMatchStatus.MISSING,
        required_degree="Bachelor's",
        required_fields=["Computer Science"],
        is_required=True,
        candidate_degree=None,
        candidate_field=None,
        degree_match=False,
        field_match=False,
        explanation="No recognized degree detected.",
    )

    recs = generate_recommendations(
        parsed_jd=base_parsed_jd,
        matched_skills=[],
        education_match=edu_match,
    )

    assert len(recs) == 1
    rec = recs[0]
    assert rec.category == RecommendationCategory.EDUCATION
    assert rec.priority == RecommendationPriority.HIGH
    assert "Mandatory Education" in rec.title
    assert any("accredited" in action.lower() or "certifications" in action.lower() for action in rec.suggested_actions)
    assert not any("change" in action.lower() or "fake" in action.lower() for action in rec.suggested_actions)


def test_preferred_education_gap(base_parsed_jd):
    """Missing preferred degree produces LOW priority recommendation."""
    edu_match = EducationMatchResult(
        status=EducationMatchStatus.MISSING,
        required_degree="Master's",
        required_fields=["Computer Science"],
        is_required=False,
        candidate_degree="Bachelor's",
        candidate_field="Computer Science",
        degree_match=False,
        field_match=True,
        explanation="Preferred Master's degree not found.",
    )

    recs = generate_recommendations(
        parsed_jd=base_parsed_jd,
        matched_skills=[],
        education_match=edu_match,
    )

    assert len(recs) == 1
    rec = recs[0]
    assert rec.category == RecommendationCategory.EDUCATION
    assert rec.priority == RecommendationPriority.LOW
    assert "Preferred Education" in rec.title


def test_duplicate_recommendation_suppression(base_parsed_jd):
    """Multiple identical missing skill items are deduplicated to a single recommendation."""
    matched_skills = [
        SkillMatchItem(
            skill="Docker",
            requirement_type=SkillRequirementType.REQUIRED,
            status=SkillMatchStatus.MISSING,
        ),
        SkillMatchItem(
            skill="Docker",
            requirement_type=SkillRequirementType.REQUIRED,
            status=SkillMatchStatus.MISSING,
        ),
    ]

    recs = generate_recommendations(
        parsed_jd=base_parsed_jd,
        matched_skills=matched_skills,
    )

    docker_recs = [r for r in recs if r.related_requirement == "Docker"]
    assert len(docker_recs) == 1


def test_priority_ordering(base_parsed_jd):
    """Recommendations are strictly sorted HIGH -> MEDIUM -> LOW."""
    matched_skills = [
        SkillMatchItem(
            skill="Redis",
            requirement_type=SkillRequirementType.PREFERRED,
            status=SkillMatchStatus.MISSING,
        ),
        SkillMatchItem(
            skill="Docker",
            requirement_type=SkillRequirementType.REQUIRED,
            status=SkillMatchStatus.MISSING,
        ),
        SkillMatchItem(
            skill="FastAPI",
            requirement_type=SkillRequirementType.REQUIRED,
            status=SkillMatchStatus.SEMANTICALLY_RELATED,
            candidate_evidence="Django",
        ),
    ]

    recs = generate_recommendations(
        parsed_jd=base_parsed_jd,
        matched_skills=matched_skills,
    )

    assert len(recs) == 3
    assert recs[0].priority == RecommendationPriority.HIGH  # Docker
    assert recs[1].priority == RecommendationPriority.MEDIUM  # FastAPI
    assert recs[2].priority == RecommendationPriority.LOW  # Redis


def test_evidence_preservation(base_parsed_jd):
    """Recommendations preserve candidate evidence when available."""
    matched_skills = [
        SkillMatchItem(
            skill="Kubernetes",
            requirement_type=SkillRequirementType.REQUIRED,
            status=SkillMatchStatus.SEMANTICALLY_RELATED,
            candidate_evidence="Docker Swarm",
        ),
    ]

    recs = generate_recommendations(
        parsed_jd=base_parsed_jd,
        matched_skills=matched_skills,
    )

    assert len(recs) == 1
    assert recs[0].candidate_evidence == "Docker Swarm"


def test_empty_recommendation_result(base_parsed_jd):
    """Fully qualified candidate produces an empty recommendation list."""
    matched_skills = [
        SkillMatchItem(
            skill="Python",
            requirement_type=SkillRequirementType.REQUIRED,
            status=SkillMatchStatus.EXACT_MATCH,
        ),
        SkillMatchItem(
            skill="Docker",
            requirement_type=SkillRequirementType.REQUIRED,
            status=SkillMatchStatus.EXACT_MATCH,
        ),
        SkillMatchItem(
            skill="AWS",
            requirement_type=SkillRequirementType.REQUIRED,
            status=SkillMatchStatus.EXACT_MATCH,
        ),
        SkillMatchItem(
            skill="Redis",
            requirement_type=SkillRequirementType.PREFERRED,
            status=SkillMatchStatus.EXACT_MATCH,
        ),
    ]
    exp_match = ExperienceMatchResult(
        assessment=ExperienceAssessmentStatus.EXCEEDS_REQUIREMENT,
        required_years=3.0,
        professional_years=4.0,
        internship_years=0.0,
        project_evidence=[{"title": "P1"}, {"title": "P2"}, {"title": "P3"}],
        relevant_responsibilities=["Design and maintain backend microservices."],
        explanation="Candidate meets all experience requirements.",
    )
    edu_match = EducationMatchResult(
        status=EducationMatchStatus.EXACT_MATCH,
        required_degree="Bachelor's",
        required_fields=["Computer Science"],
        is_required=True,
        candidate_degree="Bachelor's",
        candidate_field="Computer Science",
        degree_match=True,
        field_match=True,
        explanation="Exact degree and field match.",
    )

    recs = generate_recommendations(
        parsed_jd=base_parsed_jd,
        matched_skills=matched_skills,
        experience_match=exp_match,
        education_match=edu_match,
    )

    assert recs == []


def test_missing_or_insufficient_data_handling(base_parsed_jd):
    """Functions gracefully when optional inputs are None or empty."""
    recs = generate_recommendations(
        parsed_jd=base_parsed_jd,
        matched_skills=[],
        experience_match=None,
        education_match=None,
        score_breakdown=None,
    )

    assert isinstance(recs, list)
    assert recs == []


def test_related_skill_safety_does_not_suggest_direct_resume_addition(base_parsed_jd):
    """Related skill recommendations must require hands-on demonstration before listing on resume."""
    matched_skills = [
        SkillMatchItem(
            skill="Kubernetes",
            requirement_type=SkillRequirementType.REQUIRED,
            status=SkillMatchStatus.SEMANTICALLY_RELATED,
            candidate_evidence="Docker",
        ),
    ]

    recs = generate_recommendations(
        parsed_jd=base_parsed_jd,
        matched_skills=matched_skills,
    )

    assert len(recs) == 1
    rec = recs[0]
    # Verify actions do not blindly say "add to resume" without completing projects/verifiable proof
    assert any("Only after" in action or "verifiable" in action for action in rec.suggested_actions)
    assert any("project" in action.lower() or "microservice" in action.lower() for action in rec.suggested_actions)


def test_missing_skill_safety_does_not_suggest_faking_experience(base_parsed_jd):
    """Missing skill recommendations must focus on practical learning and building deliverables first."""
    matched_skills = [
        SkillMatchItem(
            skill="Rust",
            requirement_type=SkillRequirementType.REQUIRED,
            status=SkillMatchStatus.MISSING,
        ),
    ]

    recs = generate_recommendations(
        parsed_jd=base_parsed_jd,
        matched_skills=matched_skills,
    )

    assert len(recs) == 1
    rec = recs[0]
    # Verify actions specify building working deliverables before updating profile
    assert any("working deliverables" in action.lower() or "after completing" in action.lower() for action in rec.suggested_actions)
