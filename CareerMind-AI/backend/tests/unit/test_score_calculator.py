"""
Unit tests for Explainable Match Scoring Engine (Phase 5.4).

Tests:
- All components available (full calculation)
- Required skills fully matched (100% component score)
- Required skills partially matched (related skills give partial credit)
- Missing mandatory skills (reduces score noticeably)
- Preferred skills missing
- Experience unavailable (weight re-normalized)
- Education unavailable (weight re-normalized)
- Lexical component unavailable
- All components unavailable (safe zero score, no crash)
- Weight normalization mathematics and redistribution
- Strict score boundary enforcement (0.0 to 100.0)
- Component contribution sum consistency
- Invalid weight configurations (negative, wrong sum, missing keys)
- Lexical similarity engine
"""

import pytest
from schemas.candidate_schema import (
    CandidateProfile,
    TechnicalSkills,
    ExperienceEntry,
    EducationEntry,
)
from schemas.matching_schema import (
    ParsedJobDescription,
    SkillMatchItem,
    SkillRequirementType,
    SkillMatchStatus,
    ExperienceMatchResult,
    ExperienceAssessmentStatus,
    EducationMatchResult,
    EducationMatchStatus,
    ComponentAvailability,
    MatchScoreBreakdown,
)
from matching_engine.score_calculator import (
    calculate_match_score,
    validate_weights,
    DEFAULT_WEIGHTS,
)
from matching_engine.lexical_matcher import calculate_lexical_similarity


def _build_dummy_jd() -> ParsedJobDescription:
    """Helper fixture to construct a minimal ParsedJobDescription."""
    return ParsedJobDescription(
        raw_text="Looking for a Python and FastAPI Backend Engineer with Docker and AWS experience.",
        job_title="Backend Engineer",
        required_skills=["Python", "FastAPI"],
        preferred_skills=["Docker", "AWS"],
    )


def test_lexical_similarity_identical_text():
    """Verify high lexical similarity on identical or highly overlapping text."""
    text_a = "Senior Software Engineer with Python, FastAPI, Docker, and PostgreSQL experience."
    text_b = "Looking for a Senior Software Engineer skilled in Python, FastAPI, Docker, and PostgreSQL."
    score, top_terms = calculate_lexical_similarity(text_a, text_b)

    assert score > 75.0
    assert len(top_terms) >= 3
    assert any("python" in t.lower() for t in top_terms)


def test_lexical_similarity_disjoint_text():
    """Verify near-zero lexical similarity on disjoint domains."""
    text_a = "Chef and culinary specialist preparing French pastries and gourmet dishes."
    text_b = "Kubernetes DevOps platform engineer configuring Terraform and AWS cloud clusters."
    score, top_terms = calculate_lexical_similarity(text_a, text_b)

    assert score < 10.0


def test_validate_weights_valid():
    """Verify that default weights pass validation."""
    validate_weights(DEFAULT_WEIGHTS)


def test_validate_weights_invalid_sum():
    """Verify that weights not summing to 1.0 raise ValueError."""
    bad_weights = dict(DEFAULT_WEIGHTS)
    bad_weights["required_skills"] = 0.80  # sum = 1.40
    with pytest.raises(ValueError, match="must sum to 1.0"):
        validate_weights(bad_weights)


def test_validate_weights_negative():
    """Verify that negative weight raises ValueError."""
    bad_weights = dict(DEFAULT_WEIGHTS)
    bad_weights["required_skills"] = -0.10
    bad_weights["preferred_skills"] = 0.65
    with pytest.raises(ValueError, match="cannot be negative"):
        validate_weights(bad_weights)


def test_validate_weights_missing_keys():
    """Verify that missing component keys raise ValueError."""
    incomplete = {"required_skills": 0.5, "experience": 0.5}
    with pytest.raises(ValueError, match="Missing required component weights"):
        validate_weights(incomplete)


def test_all_components_available_strong_match():
    """Verify end-to-end score calculation when all 5 dimensions are fully satisfied."""
    jd = _build_dummy_jd()

    skill_matches = [
        SkillMatchItem(
            skill="Python",
            requirement_type=SkillRequirementType.REQUIRED,
            status=SkillMatchStatus.EXACT_MATCH,
            candidate_evidence="Python",
        ),
        SkillMatchItem(
            skill="FastAPI",
            requirement_type=SkillRequirementType.REQUIRED,
            status=SkillMatchStatus.EXACT_MATCH,
            candidate_evidence="FastAPI",
        ),
        SkillMatchItem(
            skill="Docker",
            requirement_type=SkillRequirementType.PREFERRED,
            status=SkillMatchStatus.EXACT_MATCH,
            candidate_evidence="Docker",
        ),
        SkillMatchItem(
            skill="AWS",
            requirement_type=SkillRequirementType.PREFERRED,
            status=SkillMatchStatus.EXACT_MATCH,
            candidate_evidence="AWS",
        ),
    ]

    exp_match = ExperienceMatchResult(
        required_years=3.0,
        professional_years=4.0,
        assessment=ExperienceAssessmentStatus.MEETS_REQUIREMENT,
        explanation="Candidate has 4.0 years of experience.",
    )

    edu_match = EducationMatchResult(
        required_degree="Bachelor",
        candidate_degree="Bachelor of Science",
        status=EducationMatchStatus.EXACT_MATCH,
        degree_match=True,
        field_match=True,
        explanation="Degree requirements met.",
    )

    candidate_text = "Python FastAPI Docker AWS Backend Engineer"

    breakdown = calculate_match_score(
        parsed_jd=jd,
        skill_matches=skill_matches,
        experience_match=exp_match,
        education_match=edu_match,
        candidate_text=candidate_text,
    )

    assert isinstance(breakdown, MatchScoreBreakdown)
    assert breakdown.overall_score >= 80.0
    assert breakdown.match_classification == "Strong Match"
    assert breakdown.weight_normalization_applied is False

    # Check that all components are available with 100% raw scores (except lexical which depends on cosine)
    assert breakdown.components["required_skills"].raw_score == 100.0
    assert breakdown.components["preferred_skills"].raw_score == 100.0
    assert breakdown.components["experience"].raw_score == 100.0
    assert breakdown.components["education"].raw_score == 100.0


def test_semantically_related_skills_give_partial_credit():
    """Verify that semantically related skills receive partial credit (0.5), not full credit."""
    jd = _build_dummy_jd()

    skill_matches = [
        SkillMatchItem(
            skill="Python",
            requirement_type=SkillRequirementType.REQUIRED,
            status=SkillMatchStatus.EXACT_MATCH,
            candidate_evidence="Python",
        ),
        SkillMatchItem(
            skill="FastAPI",
            requirement_type=SkillRequirementType.REQUIRED,
            status=SkillMatchStatus.SEMANTICALLY_RELATED,  # 0.5 credit
            candidate_evidence="Django (Python Web Frameworks)",
        ),
    ]

    exp_match = ExperienceMatchResult(
        assessment=ExperienceAssessmentStatus.NOT_REQUIRED,
        explanation="Not required",
    )
    edu_match = EducationMatchResult(
        status=EducationMatchStatus.NOT_REQUIRED,
        explanation="Not required",
    )

    breakdown = calculate_match_score(
        parsed_jd=jd,
        skill_matches=skill_matches,
        experience_match=exp_match,
        education_match=edu_match,
        candidate_text="Python Django",
    )

    # Required skills score: (1.0 + 0.5) / 2 = 75.0%
    req_comp = breakdown.components["required_skills"]
    assert req_comp.raw_score == 75.0


def test_missing_mandatory_skills_reduces_score():
    """Verify that missing mandatory skills drop the required skills component score to 0.0."""
    jd = _build_dummy_jd()

    skill_matches = [
        SkillMatchItem(
            skill="Python",
            requirement_type=SkillRequirementType.REQUIRED,
            status=SkillMatchStatus.MISSING,
        ),
        SkillMatchItem(
            skill="FastAPI",
            requirement_type=SkillRequirementType.REQUIRED,
            status=SkillMatchStatus.MISSING,
        ),
    ]

    exp_match = ExperienceMatchResult(
        assessment=ExperienceAssessmentStatus.NOT_REQUIRED,
        explanation="Not required",
    )
    edu_match = EducationMatchResult(
        status=EducationMatchStatus.NOT_REQUIRED,
        explanation="Not required",
    )

    breakdown = calculate_match_score(
        parsed_jd=jd,
        skill_matches=skill_matches,
        experience_match=exp_match,
        education_match=edu_match,
        candidate_text="",
    )

    assert breakdown.components["required_skills"].raw_score == 0.0
    assert breakdown.overall_score == 0.0
    assert breakdown.match_classification == "Low Match"


def test_weight_normalization_when_experience_and_education_unavailable():
    """Verify that unavailable components are excluded and remaining weights normalized."""
    jd = _build_dummy_jd()

    skill_matches = [
        SkillMatchItem(
            skill="Python",
            requirement_type=SkillRequirementType.REQUIRED,
            status=SkillMatchStatus.EXACT_MATCH,
        ),
        SkillMatchItem(
            skill="FastAPI",
            requirement_type=SkillRequirementType.REQUIRED,
            status=SkillMatchStatus.EXACT_MATCH,
        ),
    ]

    # Both Experience and Education are unassessed / not required by JD
    exp_match = ExperienceMatchResult(
        assessment=ExperienceAssessmentStatus.NOT_REQUIRED,
        explanation="No experience requirement specified in JD.",
    )
    edu_match = EducationMatchResult(
        status=EducationMatchStatus.NOT_REQUIRED,
        explanation="No education requirement specified in JD.",
    )

    breakdown = calculate_match_score(
        parsed_jd=jd,
        skill_matches=skill_matches,
        experience_match=exp_match,
        education_match=edu_match,
        candidate_text="Python FastAPI backend developer",
    )

    assert breakdown.weight_normalization_applied is True

    # Experience & Education must be UNAVAILABLE with raw_score None and normalized_weight 0.0
    assert breakdown.components["experience"].availability == ComponentAvailability.UNAVAILABLE
    assert breakdown.components["experience"].raw_score is None
    assert breakdown.components["experience"].normalized_weight == 0.0
    assert breakdown.components["experience"].weighted_contribution == 0.0

    assert breakdown.components["education"].availability == ComponentAvailability.UNAVAILABLE
    assert breakdown.components["education"].raw_score is None

    # Available components: required_skills (base 0.40) + lexical_relevance (base 0.10) = 0.50 available
    # Normalized weights must be: required_skills = 0.40 / 0.50 = 0.80, lexical = 0.10 / 0.50 = 0.20
    req_comp = breakdown.components["required_skills"]
    assert req_comp.normalized_weight == 0.80
    assert req_comp.weighted_contribution == 80.0  # 100 * 0.80

    # Overall score should reflect normalized distribution without penalty for omitted dimensions
    assert breakdown.overall_score >= 80.0
    assert breakdown.match_classification == "Strong Match"


def test_all_components_unavailable():
    """Verify that when no dimensions can be evaluated, system returns 0.0 safely without crashing."""
    jd = ParsedJobDescription(raw_text="")  # Empty JD

    exp_match = ExperienceMatchResult(
        assessment=ExperienceAssessmentStatus.NOT_REQUIRED,
        explanation="Not required",
    )
    edu_match = EducationMatchResult(
        status=EducationMatchStatus.NOT_REQUIRED,
        explanation="Not required",
    )

    breakdown = calculate_match_score(
        parsed_jd=jd,
        skill_matches=[],
        experience_match=exp_match,
        education_match=edu_match,
        candidate_text="",
    )

    assert breakdown.overall_score is None
    assert breakdown.match_classification == "Not assessable"
    for comp in breakdown.components.values():
        assert comp.normalized_weight == 0.0
        assert comp.weighted_contribution == 0.0


def test_score_boundaries_and_contribution_consistency():
    """Verify that the sum of contributions equals overall_score and stays strictly in [0.0, 100.0]."""
    jd = _build_dummy_jd()

    skill_matches = [
        SkillMatchItem(
            skill="Python",
            requirement_type=SkillRequirementType.REQUIRED,
            status=SkillMatchStatus.EXACT_MATCH,
        ),
        SkillMatchItem(
            skill="FastAPI",
            requirement_type=SkillRequirementType.REQUIRED,
            status=SkillMatchStatus.MISSING,
        ),
    ]

    exp_match = ExperienceMatchResult(
        required_years=4.0,
        professional_years=2.0,
        assessment=ExperienceAssessmentStatus.PARTIAL,
        explanation="2 years of experience.",
    )
    edu_match = EducationMatchResult(
        status=EducationMatchStatus.RELATED_MATCH,
        is_required=True,
        explanation="Related discipline.",
    )

    breakdown = calculate_match_score(
        parsed_jd=jd,
        skill_matches=skill_matches,
        experience_match=exp_match,
        education_match=edu_match,
        candidate_text="Python engineer with related background.",
    )

    # Bound check
    assert 0.0 <= breakdown.overall_score <= 100.0

    # Contribution sum check (difference within rounding float precision)
    contrib_sum = sum(c.weighted_contribution for c in breakdown.components.values())
    assert abs(round(contrib_sum, 1) - breakdown.overall_score) <= 0.2

