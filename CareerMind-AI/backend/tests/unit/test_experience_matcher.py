"""
Unit tests for Experience Matching Engine (Phase 5.3).

Tests:
- Professional experience meets requirement
- Professional experience falls short (partial)
- Internship-only candidate (tracked separately, 0.0 professional years)
- Project-only candidate (never counted as professional employment)
- Missing dates (safe handling without inventing numbers)
- Overlapping employment dates (merged without double-counting)
- Multiple sequential experience entries
- Missing experience requirement in JD (not_required)
- Relevant vs unrelated responsibilities identification
"""

import pytest
from schemas.candidate_schema import (
    CandidateProfile,
    ExperienceEntry,
    ProjectEntry,
)
from schemas.matching_schema import (
    ParsedJobDescription,
    ExperienceRequirement,
    EducationRequirement,
    ExperienceAssessmentStatus,
)
from matching_engine.experience_matcher import (
    match_candidate_experience,
    merge_employment_intervals,
    parse_date_to_month_index,
)


def _build_jd_with_experience(
    minimum_years: float | None = 3.0,
    level: str | None = None,
    is_required: bool = True,
    required_skills: list[str] | None = None,
) -> ParsedJobDescription:
    """Helper fixture to construct JD with experience requirements."""
    return ParsedJobDescription(
        raw_text="Sample JD text",
        job_title="Software Engineer",
        required_skills=required_skills or ["Python", "FastAPI", "Docker"],
        preferred_skills=[],
        experience_requirement=ExperienceRequirement(
            minimum_years=minimum_years,
            level=level,
            is_required=is_required,
        ),
        education_requirement=EducationRequirement(),
        responsibilities=[],
        keywords=["Microservices", "REST API"],
    )


def test_parse_date_to_month_index():
    """Verify robust month index conversion."""
    assert parse_date_to_month_index("Jan 2022") == 2022 * 12 + 1
    assert parse_date_to_month_index("December 2023", is_end=True) == 2023 * 12 + 12
    assert parse_date_to_month_index("2024", is_end=False) == 2024 * 12 + 1
    assert parse_date_to_month_index("2024", is_end=True) == 2024 * 12 + 12
    assert parse_date_to_month_index(None) is None


def test_merge_employment_intervals_no_double_counting():
    """Verify overlapping intervals merge into disjoint coverage without double-counting."""
    # Job A: Jan 2022 – Dec 2022 (months 1 to 12)
    # Job B: Jun 2022 – Dec 2022 (months 6 to 12, overlap)
    job_a = (2022 * 12 + 1, 2022 * 12 + 12)
    job_b = (2022 * 12 + 6, 2022 * 12 + 12)

    total_months = merge_employment_intervals([job_a, job_b])
    # Must be 12 months (1.0 year), NOT 19 months
    assert total_months == 12


def test_professional_experience_meets_requirement():
    """Verify candidate with sufficient professional years meets the requirement."""
    candidate = CandidateProfile(
        experience=[
            ExperienceEntry(
                job_title="Software Engineer",
                company="Tech Corp",
                start_date="Jan 2021",
                end_date="Dec 2024",  # 48 months = 4.0 years
                description="• Developed microservices using Python and FastAPI.",
            )
        ]
    )
    jd = _build_jd_with_experience(minimum_years=3.0)

    result = match_candidate_experience(candidate, jd)

    assert result.required_years == 3.0
    assert result.professional_years == 4.0
    assert result.internship_years == 0.0
    assert result.assessment == ExperienceAssessmentStatus.MEETS_REQUIREMENT
    assert "meeting the required 3.0 years" in result.explanation
    assert len(result.relevant_responsibilities) >= 1


def test_professional_experience_falls_short_partial():
    """Verify candidate with 1.5 years gets partial assessment when 3.0 years required."""
    candidate = CandidateProfile(
        experience=[
            ExperienceEntry(
                job_title="Junior Developer",
                company="Startup Inc",
                start_date="Jan 2023",
                end_date="Jun 2024",  # 18 months = 1.5 years
                description="• Built APIs.",
            )
        ]
    )
    jd = _build_jd_with_experience(minimum_years=3.0)

    result = match_candidate_experience(candidate, jd)

    assert result.professional_years == 1.5
    assert result.assessment == ExperienceAssessmentStatus.PARTIAL
    assert "falling short" in result.explanation


def test_internship_only_candidate_tracked_separately():
    """Verify internships are NOT counted as professional employment."""
    candidate = CandidateProfile(
        experience=[
            ExperienceEntry(
                job_title="Software Engineering Intern",
                company="Innovate Labs",
                employment_type="Internship",
                start_date="Jun 2024",
                end_date="Aug 2024",  # 3 months
                description="• Developed prototype.",
            )
        ]
    )
    jd = _build_jd_with_experience(minimum_years=2.0)

    result = match_candidate_experience(candidate, jd)

    # Professional years must be 0.0
    assert result.professional_years == 0.0
    assert result.internship_years == 0.2  # 3 months ~ 0.2 yrs
    assert len(result.internship_entries) == 1
    assert result.assessment == ExperienceAssessmentStatus.BELOW_REQUIREMENT
    assert "0.0 years of professional employment" in result.explanation


def test_project_only_candidate_never_counts_as_employment():
    """Verify projects are never credited as professional employment years."""
    candidate = CandidateProfile(
        experience=[],
        projects=[
            ProjectEntry(
                project_name="Cloud Platform",
                technologies=["Python", "FastAPI", "Docker"],
                description="Built full-stack microservices application.",
            )
        ],
    )
    jd = _build_jd_with_experience(minimum_years=2.0)

    result = match_candidate_experience(candidate, jd)

    assert result.professional_years == 0.0
    assert result.internship_years == 0.0
    assert len(result.project_evidence) == 1
    assert result.project_evidence[0]["project_name"] == "Cloud Platform"
    assert result.assessment == ExperienceAssessmentStatus.BELOW_REQUIREMENT


def test_missing_dates_handled_safely():
    """Verify that roles without dates flag missing_information and yield insufficient_data."""
    candidate = CandidateProfile(
        experience=[
            ExperienceEntry(
                job_title="Backend Developer",
                company="Undated Solutions",
                start_date=None,
                end_date=None,
                description="• Built services.",
            )
        ]
    )
    jd = _build_jd_with_experience(minimum_years=3.0)

    result = match_candidate_experience(candidate, jd)

    assert result.professional_years is None
    assert result.assessment == ExperienceAssessmentStatus.INSUFFICIENT_DATA
    assert len(result.missing_information) == 1
    assert "Employment dates not specified" in result.missing_information[0]


def test_multiple_sequential_roles_sum_accurately():
    """Verify multiple non-overlapping roles are summed correctly."""
    candidate = CandidateProfile(
        experience=[
            ExperienceEntry(
                job_title="Backend Engineer",
                company="Company A",
                start_date="Jan 2021",
                end_date="Dec 2022",  # 24 months = 2.0 yrs
            ),
            ExperienceEntry(
                job_title="Senior Engineer",
                company="Company B",
                start_date="Jan 2023",
                end_date="Dec 2024",  # 24 months = 2.0 yrs
            ),
        ]
    )
    jd = _build_jd_with_experience(minimum_years=3.0)

    result = match_candidate_experience(candidate, jd)

    assert result.professional_years == 4.0
    assert result.assessment == ExperienceAssessmentStatus.MEETS_REQUIREMENT


def test_no_experience_requirement_in_jd():
    """Verify not_required assessment when JD has no experience expectations."""
    candidate = CandidateProfile(
        experience=[
            ExperienceEntry(
                job_title="Developer",
                company="Acme",
                start_date="Jan 2024",
                end_date="Dec 2024",
            )
        ]
    )
    jd = _build_jd_with_experience(minimum_years=None, level=None, is_required=False)

    result = match_candidate_experience(candidate, jd)

    assert result.assessment == ExperienceAssessmentStatus.NOT_REQUIRED
    assert result.is_required is False


def test_relevant_and_unrelated_responsibilities_separated():
    """Verify technical bullets matching JD are separated from unrelated responsibilities."""
    candidate = CandidateProfile(
        experience=[
            ExperienceEntry(
                job_title="Software Developer",
                company="Fintech Corp",
                description=(
                    "• Built REST APIs and microservices using Python.\n"
                    "• Organized catering and decorations for annual office retreat.\n"
                    "• Deployed containerized applications with Docker."
                ),
            )
        ]
    )
    jd = _build_jd_with_experience(
        minimum_years=1.0,
        required_skills=["Python", "Docker"],
    )

    result = match_candidate_experience(candidate, jd)

    assert len(result.relevant_responsibilities) == 2
    assert any("REST APIs and microservices" in r for r in result.relevant_responsibilities)
    assert any("containerized applications" in r for r in result.relevant_responsibilities)

    assert len(result.unrelated_responsibilities) == 1
    assert any("catering and decorations" in u for u in result.unrelated_responsibilities)

