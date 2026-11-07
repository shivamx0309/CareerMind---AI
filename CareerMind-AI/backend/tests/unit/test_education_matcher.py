"""
Unit tests for Education Matching Engine (Phase 5.3).

Tests:
- Exact degree and field of study match
- Higher degree satisfying lower requirement (e.g. Master satisfies Bachelor)
- Related discipline match (e.g. Information Technology satisfies Computer Science as related)
- Missing degree when candidate degree is lower than mandatory requirement
- Preferred degree when candidate degree is lower but requirement was optional
- No education requirement in JD (not_required)
- Candidate profile with missing education (missing)
- CGPA integrity: grade/CGPA is never invented when absent
- Insufficient education data when degree is undefined
"""

import pytest
from schemas.candidate_schema import (
    CandidateProfile,
    EducationEntry,
)
from schemas.matching_schema import (
    ParsedJobDescription,
    EducationRequirement,
    ExperienceRequirement,
    EducationMatchStatus,
)
from matching_engine.education_matcher import (
    match_candidate_education,
    normalize_degree_level,
)


def _build_jd_with_education(
    required_degree: str | None = "Bachelor",
    fields_of_study: list[str] | None = None,
    is_required: bool = True,
) -> ParsedJobDescription:
    """Helper fixture to construct JD with education expectations."""
    return ParsedJobDescription(
        raw_text="Sample JD text",
        job_title="Software Engineer",
        required_skills=[],
        preferred_skills=[],
        experience_requirement=ExperienceRequirement(),
        education_requirement=EducationRequirement(
            required_degree=required_degree,
            fields_of_study=fields_of_study if fields_of_study is not None else ["Computer Science"],
            is_required=is_required,
        ),
        responsibilities=[],
        keywords=[],
    )


def test_normalize_degree_level():
    """Verify standard degree normalization across varied formats."""
    assert normalize_degree_level("Bachelor of Engineering") == "Bachelor"
    assert normalize_degree_level("B.Tech in CS") == "Bachelor"
    assert normalize_degree_level("Master of Science") == "Master"
    assert normalize_degree_level("Ph.D. in AI") == "PhD"
    assert normalize_degree_level("Diploma in Computer Engineering") == "Associate"
    assert normalize_degree_level(None) is None


def test_exact_degree_and_field_match():
    """Verify exact match when degree level and field of study match."""
    candidate = CandidateProfile(
        education=[
            EducationEntry(
                degree="Bachelor of Technology",
                institution="National Institute of Technology",
                specialization="Computer Science",
                grade_or_cgpa="8.5 / 10",
            )
        ]
    )
    jd = _build_jd_with_education(
        required_degree="Bachelor",
        fields_of_study=["Computer Science"],
    )

    result = match_candidate_education(candidate, jd)

    assert result.status == EducationMatchStatus.EXACT_MATCH
    assert result.degree_match is True
    assert result.field_match is True
    assert result.candidate_degree == "Bachelor of Technology"
    assert result.candidate_grade == "8.5 / 10"  # Preserved verbatim
    assert "fully meeting" in result.explanation


def test_higher_degree_satisfies_requirement():
    """Verify that a Master's degree satisfies a Bachelor's requirement."""
    candidate = CandidateProfile(
        education=[
            EducationEntry(
                degree="Master of Science in Computer Science",
                institution="Stanford University",
                specialization="Computer Science",
            )
        ]
    )
    jd = _build_jd_with_education(
        required_degree="Bachelor",
        fields_of_study=["Computer Science"],
    )

    result = match_candidate_education(candidate, jd)

    assert result.status == EducationMatchStatus.EXACT_MATCH
    assert result.degree_match is True


def test_related_field_match():
    """Verify that a degree in Information Technology is recognized as related to Computer Science."""
    candidate = CandidateProfile(
        education=[
            EducationEntry(
                degree="Bachelor of Engineering",
                institution="Tech University",
                specialization="Information Technology",
            )
        ]
    )
    jd = _build_jd_with_education(
        required_degree="Bachelor",
        fields_of_study=["Computer Science"],
    )

    result = match_candidate_education(candidate, jd)

    # Degree level matched, but field is related rather than exact
    assert result.status == EducationMatchStatus.RELATED_MATCH
    assert result.degree_match is True
    assert result.field_match is True
    assert "related discipline" in result.explanation


def test_missing_degree_lower_level():
    """Verify missing status when candidate holds a Bachelor's but Master's is mandatory."""
    candidate = CandidateProfile(
        education=[
            EducationEntry(
                degree="Bachelor of Science",
                institution="State University",
                specialization="Computer Science",
            )
        ]
    )
    jd = _build_jd_with_education(
        required_degree="Master",
        fields_of_study=["Computer Science"],
        is_required=True,
    )

    result = match_candidate_education(candidate, jd)

    assert result.status == EducationMatchStatus.MISSING
    assert result.degree_match is False
    assert "Role requires a Master" in result.explanation


def test_preferred_degree_lower_level():
    """Verify related_match when candidate degree is lower than preferred optional requirement."""
    candidate = CandidateProfile(
        education=[
            EducationEntry(
                degree="Bachelor of Science",
                institution="State University",
                specialization="Computer Science",
            )
        ]
    )
    jd = _build_jd_with_education(
        required_degree="Master",
        fields_of_study=["Computer Science"],
        is_required=False,  # Optional / preferred
    )

    result = match_candidate_education(candidate, jd)

    # Not penalized as missing because requirement was optional
    assert result.status == EducationMatchStatus.RELATED_MATCH
    assert result.is_required is False


def test_no_education_requirement_in_jd():
    """Verify not_required status when JD does not specify any education expectations."""
    candidate = CandidateProfile(
        education=[
            EducationEntry(
                degree="Bachelor of Arts",
                institution="College",
            )
        ]
    )
    jd = _build_jd_with_education(
        required_degree=None,
        fields_of_study=[],
    )

    result = match_candidate_education(candidate, jd)

    assert result.status == EducationMatchStatus.NOT_REQUIRED
    assert result.degree_match is True
    assert "does not specify" in result.explanation


def test_missing_candidate_education():
    """Verify missing status when candidate has empty education history."""
    candidate = CandidateProfile(education=[])
    jd = _build_jd_with_education(required_degree="Bachelor")

    result = match_candidate_education(candidate, jd)

    assert result.status == EducationMatchStatus.MISSING
    assert result.degree_match is False
    assert result.candidate_degree is None


def test_missing_cgpa_never_invented():
    """Verify that when grade_or_cgpa is None, the system leaves candidate_grade as None."""
    candidate = CandidateProfile(
        education=[
            EducationEntry(
                degree="Bachelor of Technology",
                institution="University",
                specialization="Computer Science",
                grade_or_cgpa=None,
            )
        ]
    )
    jd = _build_jd_with_education(required_degree="Bachelor")

    result = match_candidate_education(candidate, jd)

    assert result.candidate_grade is None


def test_insufficient_education_data():
    """Verify insufficient_data when candidate education entry has undefined degree."""
    candidate = CandidateProfile(
        education=[
            EducationEntry(
                degree=None,
                institution="Some Institute",
            )
        ]
    )
    jd = _build_jd_with_education(required_degree="Bachelor")

    result = match_candidate_education(candidate, jd)

    assert result.status == EducationMatchStatus.INSUFFICIENT_DATA
    assert result.degree_match is False

