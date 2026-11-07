"""
Experience Matching Engine for CareerMind AI (Phase 5.3).

Evaluates candidate work, internship, and project experience against structured JD requirements:
- Distinguishes professional work experience from internship and project experience.
- Merges overlapping employment intervals to prevent double-counting.
- Compares job responsibilities and technical depth, not just designations.
- Handles missing dates safely without inventing numbers.
- Separates relevant responsibilities from unrelated responsibilities.
- Avoids inferring seniority from a job title alone.
"""

import re
from schemas.candidate_schema import CandidateProfile, ExperienceEntry
from schemas.matching_schema import (
    ParsedJobDescription,
    ExperienceMatchResult,
    ExperienceAssessmentStatus,
)


MONTH_MAP = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "september": 9, "sept": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}

CURRENT_REF_YEAR = 2026
CURRENT_REF_MONTH = 11


def parse_date_to_month_index(date_str: str | None, is_end: bool = False) -> int | None:
    """
    Parse a date string into an integer month index (year * 12 + month).

    Handles:
    - 'June 2026', 'Jun 2026', '06/2026'
    - '2024' (defaults to Jan for start, Dec for end)
    - 'Present', 'Current' (uses reference date)
    """
    if not date_str or not date_str.strip():
        return None

    cleaned = date_str.strip().lower()

    if cleaned in ("present", "current", "now", "ongoing"):
        return CURRENT_REF_YEAR * 12 + CURRENT_REF_MONTH

    # Check "Month Year" (e.g. "June 2026", "Jun 2024")
    m_month_year = re.search(r"\b([a-zA-Z]{3,9})\.?\s+(\d{4})\b", cleaned)
    if m_month_year:
        m_str, y_str = m_month_year.group(1), m_month_year.group(2)
        month_num = MONTH_MAP.get(m_str[:3], 1 if not is_end else 12)
        year_num = int(y_str)
        return year_num * 12 + month_num

    # Check "MM/YYYY" or "MM-YYYY"
    m_num_date = re.search(r"\b(\d{1,2})[/-](\d{4})\b", cleaned)
    if m_num_date:
        month_num = min(max(int(m_num_date.group(1)), 1), 12)
        year_num = int(m_num_date.group(2))
        return year_num * 12 + month_num

    # Check standalone "YYYY"
    m_year = re.search(r"\b(19\d{2}|20\d{2})\b", cleaned)
    if m_year:
        year_num = int(m_year.group(1))
        month_num = 12 if is_end else 1
        return year_num * 12 + month_num

    return None


def merge_employment_intervals(intervals: list[tuple[int, int]]) -> int:
    """
    Merge overlapping or adjacent month intervals and return total distinct months.

    Prevents double-counting overlapping employment periods (Requirement 10).
    """
    if not intervals:
        return 0

    # Sort intervals by start month
    sorted_intervals = sorted(intervals, key=lambda x: (x[0], x[1]))
    merged: list[tuple[int, int]] = []

    for start, end in sorted_intervals:
        if not merged:
            merged.append((start, max(start, end)))
            continue

        prev_start, prev_end = merged[-1]
        if start <= prev_end + 1:  # Overlapping or adjacent
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, max(start, end)))

    # Sum total months across disjoint intervals (+1 to include both boundary months)
    total_months = sum((end - start + 1) for start, end in merged)
    return total_months


def is_internship_entry(exp: ExperienceEntry) -> bool:
    """Determine whether an experience entry represents an internship."""
    if exp.employment_type and "intern" in exp.employment_type.lower():
        return True
    if exp.job_title and "intern" in exp.job_title.lower():
        return True
    return False


def match_candidate_experience(
    candidate: CandidateProfile,
    parsed_jd: ParsedJobDescription,
) -> ExperienceMatchResult:
    """
    Evaluate candidate professional experience, internships, and projects against JD requirements.
    """
    jd_exp = parsed_jd.experience_requirement
    required_years = jd_exp.minimum_years
    required_level = jd_exp.level
    is_required = jd_exp.is_required

    professional_intervals: list[tuple[int, int]] = []
    internship_intervals: list[tuple[int, int]] = []
    internship_entries: list[dict] = []
    missing_info: list[str] = []
    has_professional_roles = False

    # Extract target skill tokens for relevance matching
    target_skill_tokens = set(
        s.lower() for s in (parsed_jd.required_skills + parsed_jd.preferred_skills + parsed_jd.keywords)
    )

    relevant_responsibilities: list[str] = []
    unrelated_responsibilities: list[str] = []

    # 1. Evaluate Experience Entries
    for exp in candidate.experience or []:
        role_title = exp.job_title or "Role"
        company = exp.company or "Company"
        is_intern = is_internship_entry(exp)

        if not is_intern:
            has_professional_roles = True

        # Parse dates
        start_idx = parse_date_to_month_index(exp.start_date, is_end=False)
        end_idx = parse_date_to_month_index(exp.end_date, is_end=True)

        if start_idx is not None and end_idx is not None and end_idx >= start_idx:
            interval = (start_idx, end_idx)
            duration_months = end_idx - start_idx + 1

            if is_intern:
                internship_intervals.append(interval)
                internship_entries.append({
                    "job_title": role_title,
                    "company": company,
                    "duration_months": duration_months,
                    "dates": f"{exp.start_date} – {exp.end_date}",
                })
            else:
                professional_intervals.append(interval)
        else:
            if not exp.start_date or not exp.end_date:
                missing_info.append(
                    f"Employment dates not specified for '{role_title}' at '{company}'."
                )

        # Assess Responsibilities Relevance
        if exp.description:
            for line in exp.description.splitlines():
                cleaned_line = line.strip("•-*\t ")
                if not cleaned_line:
                    continue
                # Check for match against target skills or technical keywords
                line_lower = cleaned_line.lower()
                is_relevant = any(tok in line_lower for tok in target_skill_tokens)
                if is_relevant:
                    relevant_responsibilities.append(f"[{company}] {cleaned_line}")
                else:
                    unrelated_responsibilities.append(f"[{company}] {cleaned_line}")

    # Calculate distinct, non-overlapping durations
    prof_months = merge_employment_intervals(professional_intervals)
    intern_months = merge_employment_intervals(internship_intervals)

    professional_years = round(prof_months / 12.0, 1) if professional_intervals else (
        0.0 if not has_professional_roles else None
    )
    internship_years = round(intern_months / 12.0, 1) if internship_intervals else 0.0

    # 2. Evaluate Projects (Never counted as professional employment)
    project_evidence: list[dict] = []
    for proj in candidate.projects or []:
        p_name = proj.project_name or "Project"
        p_techs = proj.technologies or []
        overlap = [t for t in p_techs if t.lower() in target_skill_tokens]

        project_evidence.append({
            "project_name": p_name,
            "technologies": p_techs,
            "relevant_skills": overlap,
            "relevance": (
                f"Demonstrates practical hands-on use of {', '.join(overlap)}"
                if overlap
                else "General academic/portfolio project"
            ),
        })

    # 3. Determine Evidence Sources
    evidence_sources = []
    if professional_intervals or has_professional_roles:
        evidence_sources.append("professional_experience")
    if internship_entries:
        evidence_sources.append("internship_experience")
    if project_evidence:
        evidence_sources.append("projects")

    # 4. Formulate Assessment & Explanation
    assessment: ExperienceAssessmentStatus
    explanation: str

    if not is_required and required_years is None and required_level is None:
        assessment = ExperienceAssessmentStatus.NOT_REQUIRED
        explanation = (
            f"The job description does not specify required years of professional experience. "
            f"Candidate profile presents {professional_years or 0.0} years professional experience "
            f"and {internship_years} years internship experience."
        )
    elif professional_years is None and has_professional_roles:
        # Candidate has roles listed, but all dates are missing
        assessment = ExperienceAssessmentStatus.INSUFFICIENT_DATA
        explanation = (
            f"Candidate lists professional roles, but dates were missing or unparseable to verify duration. "
            f"Target role expects {required_years} years."
        )
    elif required_years is not None:
        if professional_years is not None and professional_years >= required_years * 1.5:
            assessment = ExperienceAssessmentStatus.EXCEEDS_REQUIREMENT
            explanation = (
                f"Candidate possesses {professional_years} years of verified professional experience, "
                f"exceeding the required {required_years} years."
            )
        elif professional_years is not None and professional_years >= required_years:
            assessment = ExperienceAssessmentStatus.MEETS_REQUIREMENT
            explanation = (
                f"Candidate possesses {professional_years} years of verified professional experience, "
                f"meeting the required {required_years} years."
            )
        elif professional_years is not None and professional_years > 0.0:
            assessment = ExperienceAssessmentStatus.PARTIAL
            explanation = (
                f"Candidate possesses {professional_years} years of professional experience, "
                f"falling short of the required {required_years} years."
            )
        else:
            # Candidate has 0.0 professional years (internships and projects only)
            assessment = ExperienceAssessmentStatus.BELOW_REQUIREMENT
            supp_details = []
            if internship_years > 0.0:
                supp_details.append(f"{internship_years} years of internship experience")
            if project_evidence:
                supp_details.append(f"{len(project_evidence)} portfolio project(s)")
            supp_str = f" (demonstrating {', '.join(supp_details)})" if supp_details else ""

            explanation = (
                f"Candidate has 0.0 years of professional employment{supp_str}, "
                f"whereas the role requires {required_years} years of professional employment experience. "
                f"Projects and internships are tracked separately and not counted as full professional employment."
            )
    elif required_level:
        # Seniority level evaluation
        if required_level in ("Lead / Principal", "Senior") and (professional_years or 0.0) < 3.0:
            assessment = ExperienceAssessmentStatus.BELOW_REQUIREMENT
            explanation = (
                f"Target role expects {required_level} level, but candidate possesses "
                f"{professional_years or 0.0} years of professional experience."
            )
        elif required_level == "Entry-level":
            assessment = ExperienceAssessmentStatus.MEETS_REQUIREMENT
            explanation = "Target role is entry-level; candidate qualifications and portfolio align with role expectations."
        else:
            assessment = ExperienceAssessmentStatus.MEETS_REQUIREMENT
            explanation = f"Candidate experience aligns with target role level ({required_level})."
    else:
        assessment = ExperienceAssessmentStatus.MEETS_REQUIREMENT
        explanation = "Candidate experience is consistent with role requirements."

    return ExperienceMatchResult(
        required_years=required_years,
        required_level=required_level,
        is_required=is_required,
        professional_years=professional_years,
        internship_years=internship_years,
        internship_entries=internship_entries,
        project_evidence=project_evidence,
        relevant_responsibilities=relevant_responsibilities,
        unrelated_responsibilities=unrelated_responsibilities,
        assessment=assessment,
        missing_information=missing_info,
        evidence_sources=evidence_sources,
        explanation=explanation,
    )

