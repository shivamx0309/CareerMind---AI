"""
Education Matching Engine for CareerMind AI (Phase 5.3).

Evaluates candidate educational qualifications against structured JD requirements:
- Compares degree level (Bachelor, Master, PhD, Associate).
- Compares field of study / specialization (exact vs related disciplines).
- Classifies into exact_match, related_match, missing, not_required, or insufficient_data.
- Never invents CGPA or grades.
- Distinguishes mandatory degree requirements from preferred qualifications.
"""

import re
from schemas.candidate_schema import CandidateProfile, EducationEntry
from schemas.matching_schema import (
    ParsedJobDescription,
    EducationMatchResult,
    EducationMatchStatus,
)


DEGREE_RANK = {
    "phd": 4,
    "doctorate": 4,
    "master": 3,
    "bachelor": 2,
    "associate": 1,
}

EXACT_DISCIPLINE_CLUSTERS = {
    "computer science": {"computer science", "computer science engineering", "cse", "cs"},
    "software engineering": {"software engineering", "software development"},
    "information technology": {"information technology", "it", "information systems"},
    "data science": {"data science", "data analytics", "business analytics"},
    "artificial intelligence": {"artificial intelligence", "ai", "machine learning"},
    "electrical engineering": {"electrical engineering", "electronics engineering", "ece", "ee"},
    "mathematics": {"mathematics", "applied mathematics", "math"},
    "statistics": {"statistics", "applied statistics"},
}

RELATED_DISCIPLINES = {
    "computer science": {"information technology", "software engineering", "data science", "electrical engineering", "mathematics"},
    "software engineering": {"computer science", "information technology", "electrical engineering"},
    "data science": {"computer science", "statistics", "mathematics", "information technology"},
}


def normalize_degree_level(degree_str: str | None) -> str | None:
    """Map arbitrary degree titles to canonical levels: PhD, Master, Bachelor, Associate."""
    if not degree_str:
        return None

    cleaned = degree_str.strip().lower()

    if re.search(r"\b(?:ph\.?d|doctorate|doctoral)\b", cleaned):
        return "PhD"
    if re.search(r"\b(?:master(?:'s)?|ms|m\.s\.?|m\.tech|msc|m\.sc\.?|post[\s-]*graduate)\b", cleaned):
        return "Master"
    if re.search(r"\b(?:bachelor(?:'s)?|bs|b\.s\.?|b\.tech|b\.e\.?|bsc|b\.sc\.?|undergraduate)\b", cleaned):
        return "Bachelor"
    if re.search(r"\b(?:associate(?:'s)?|diploma)\b", cleaned):
        return "Associate"

    return degree_str.strip()


def check_discipline_match(
    candidate_spec: str | None,
    candidate_degree: str | None,
    required_fields: list[str],
) -> tuple[bool, bool]:
    """
    Check if candidate's field of study matches required fields.

    Returns:
        (exact_match, related_match)
    """
    if not required_fields:
        return True, True

    cand_text = f"{candidate_spec or ''} {candidate_degree or ''}".lower()
    if not cand_text.strip():
        return False, False

    # Check exact discipline match
    for rf in required_fields:
        rf_clean = rf.strip().lower()
        # Direct substring
        if rf_clean in cand_text:
            return True, True
        # Cluster aliases
        cluster_synonyms = EXACT_DISCIPLINE_CLUSTERS.get(rf_clean, {rf_clean})
        if any(syn in cand_text for syn in cluster_synonyms):
            return True, True

    # Check related discipline match
    for rf in required_fields:
        rf_clean = rf.strip().lower()
        related_set = RELATED_DISCIPLINES.get(rf_clean, set())
        if any(rel in cand_text for rel in related_set):
            return False, True

    return False, False


def match_candidate_education(
    candidate: CandidateProfile,
    parsed_jd: ParsedJobDescription,
) -> EducationMatchResult:
    """
    Evaluate candidate educational credentials against JD expectations.
    """
    edu_req = parsed_jd.education_requirement
    required_degree = edu_req.required_degree
    required_fields = edu_req.fields_of_study
    is_required = edu_req.is_required

    # 1. JD has no education requirement
    if not required_degree and not required_fields:
        cand_edu = (candidate.education or [None])[0]
        return EducationMatchResult(
            required_degree=None,
            required_fields=[],
            is_required=False,
            candidate_degree=cand_edu.degree if cand_edu else None,
            candidate_field=cand_edu.specialization if cand_edu else None,
            candidate_institution=cand_edu.institution if cand_edu else None,
            candidate_grade=cand_edu.grade_or_cgpa if cand_edu else None,
            status=EducationMatchStatus.NOT_REQUIRED,
            degree_match=True,
            field_match=True,
            evidence=None,
            explanation="The job description does not specify mandatory or preferred education requirements.",
        )

    # 2. Candidate has no educational entries
    if not candidate.education:
        return EducationMatchResult(
            required_degree=required_degree,
            required_fields=required_fields,
            is_required=is_required,
            candidate_degree=None,
            candidate_field=None,
            candidate_institution=None,
            candidate_grade=None,
            status=EducationMatchStatus.MISSING if is_required else EducationMatchStatus.RELATED_MATCH,
            degree_match=False,
            field_match=False,
            evidence=None,
            explanation=(
                f"Candidate profile does not contain educational credentials to verify required "
                f"{required_degree or 'degree'}."
            ),
        )

    # 3. Find the candidate's highest / best-matching qualification
    best_entry: EducationEntry | None = None
    best_degree_level: str | None = None
    best_rank = -1
    best_exact_field = False
    best_related_field = False

    for entry in candidate.education:
        level = normalize_degree_level(entry.degree)
        rank = DEGREE_RANK.get((level or "").lower(), 0)
        is_exact, is_related = check_discipline_match(
            entry.specialization,
            entry.degree,
            required_fields,
        )

        if rank > best_rank or (rank == best_rank and is_exact and not best_exact_field):
            best_entry = entry
            best_degree_level = level
            best_rank = rank
            best_exact_field = is_exact
            best_related_field = is_related

    if not best_entry or not best_degree_level:
        return EducationMatchResult(
            required_degree=required_degree,
            required_fields=required_fields,
            is_required=is_required,
            candidate_degree=None,
            candidate_field=None,
            candidate_institution=None,
            candidate_grade=None,
            status=EducationMatchStatus.INSUFFICIENT_DATA,
            degree_match=False,
            field_match=False,
            evidence=None,
            explanation="Candidate lists education entries, but degree level could not be identified.",
        )

    required_rank = DEGREE_RANK.get((required_degree or "").lower(), 0)
    degree_satisfied = best_rank >= required_rank if required_degree else True
    field_satisfied = best_exact_field or best_related_field or not required_fields

    cand_evidence = f"{best_entry.degree or ''} from {best_entry.institution or 'institution'}"
    if best_entry.specialization:
        cand_evidence = f"{cand_evidence} ({best_entry.specialization})"

    # 4. Determine Classification Status
    status: EducationMatchStatus
    explanation: str

    if degree_satisfied and best_exact_field:
        status = EducationMatchStatus.EXACT_MATCH
        explanation = (
            f"Candidate holds a {best_degree_level} in {best_entry.specialization or 'relevant field'} "
            f"from {best_entry.institution or 'accredited institution'}, fully meeting the "
            f"{required_degree or 'degree'} requirement."
        )
    elif degree_satisfied and best_related_field:
        status = EducationMatchStatus.RELATED_MATCH
        explanation = (
            f"Candidate holds a {best_degree_level} in a related discipline "
            f"({best_entry.specialization or 'related engineering'}), satisfying the degree level requirement."
        )
    elif not is_required and degree_satisfied:
        status = EducationMatchStatus.RELATED_MATCH
        explanation = (
            f"Candidate holds a {best_degree_level}, meeting the preferred {required_degree} requirement."
        )
    elif not degree_satisfied:
        if not is_required:
            status = EducationMatchStatus.RELATED_MATCH
            explanation = (
                f"Candidate holds a {best_degree_level}, which is below the preferred {required_degree}."
            )
        else:
            status = EducationMatchStatus.MISSING
            explanation = (
                f"Role requires a {required_degree}, but candidate holds a {best_degree_level}."
            )
    else:
        status = EducationMatchStatus.RELATED_MATCH
        explanation = f"Candidate education partially aligns with role expectations."

    return EducationMatchResult(
        required_degree=required_degree,
        required_fields=required_fields,
        is_required=is_required,
        candidate_degree=best_entry.degree,
        candidate_field=best_entry.specialization,
        candidate_institution=best_entry.institution,
        candidate_grade=best_entry.grade_or_cgpa,  # Never invented
        status=status,
        degree_match=degree_satisfied,
        field_match=field_satisfied,
        evidence=cand_evidence,
        explanation=explanation,
    )

