"""
Explainable Match Scoring Engine for CareerMind AI (Phase 5.4).

Combines evaluations from:
1. Required Skills Matching (Default weight: 40%)
2. Preferred Skills Matching (Default weight: 15%)
3. Experience Relevance Matching (Default weight: 25%)
4. Education Alignment Matching (Default weight: 10%)
5. Lexical Relevance Matching (Default weight: 10%)

Key Architectural Properties:
- Explicit Availability Tracking: Distinguishes genuine gaps from unavailable data.
- Weight Normalization: Excludes unavailable components from the denominator and re-normalizes available weights.
- Zero Double-Counting: Each component and evidence source is evaluated once.
- Strictly Bounded: Final score is guaranteed to remain in [0.0, 100.0].
- Transparent & Explainable: Detailed human-readable narrative and evidence for every component.
"""

from schemas.candidate_schema import CandidateProfile
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
    ComponentScore,
    MatchScoreBreakdown,
)
from matching_engine.lexical_matcher import calculate_lexical_similarity


DEFAULT_WEIGHTS = {
    "required_skills": 0.40,
    "preferred_skills": 0.15,
    "experience": 0.25,
    "education": 0.10,
    "lexical_relevance": 0.10,
}


def validate_weights(weights: dict[str, float]) -> None:
    """Validate that weights are non-negative and sum to 1.0."""
    required_keys = {"required_skills", "preferred_skills", "experience", "education", "lexical_relevance"}
    missing = required_keys - set(weights.keys())
    if missing:
        raise ValueError(f"Missing required component weights: {missing}")

    for k, v in weights.items():
        if v < 0.0:
            raise ValueError(f"Component weight for '{k}' cannot be negative: {v}")

    total_weight = sum(weights.values())
    if abs(total_weight - 1.0) > 1e-4:
        raise ValueError(
            f"Component weights must sum to 1.0 (current sum: {round(total_weight, 4)})"
        )


def _build_candidate_full_text(candidate: CandidateProfile | None) -> str:
    """Aggregate all searchable prose and skills from candidate profile for lexical comparison."""
    if not candidate:
        return ""

    chunks: list[str] = []
    if candidate.professional_summary:
        chunks.append(candidate.professional_summary)

    # Technical Skills
    ts = candidate.technical_skills
    if ts:
        for cat in (
            "programming_languages", "frontend", "backend", "databases",
            "data_analytics", "machine_learning", "deep_learning",
            "cloud_devops", "tools", "other",
        ):
            skills = getattr(ts, cat, []) or []
            if skills:
                chunks.append(" ".join(skills))

    # Experience
    for exp in candidate.experience or []:
        if exp.job_title:
            chunks.append(exp.job_title)
        if exp.technologies:
            chunks.append(" ".join(exp.technologies))
        if exp.description:
            chunks.append(exp.description)

    # Projects
    for proj in candidate.projects or []:
        if proj.project_name:
            chunks.append(proj.project_name)
        if proj.technologies:
            chunks.append(" ".join(proj.technologies))
        if proj.description:
            chunks.append(proj.description)

    # Certifications
    for cert in candidate.certifications or []:
        if cert.certification_name:
            chunks.append(cert.certification_name)

    return " ".join(chunks)


def evaluate_required_skills_component(
    skill_matches: list[SkillMatchItem],
    base_weight: float,
) -> tuple[ComponentAvailability, float | None, list[str], str]:
    """Evaluate Required Skills dimension."""
    req_items = [m for m in skill_matches if m.requirement_type == SkillRequirementType.REQUIRED]

    if not req_items:
        return (
            ComponentAvailability.UNAVAILABLE,
            None,
            [],
            "Job description does not specify required technical skills.",
        )

    total_credit = 0.0
    evidence: list[str] = []
    exact_count = 0
    alias_count = 0
    related_count = 0
    missing_count = 0

    for item in req_items:
        if item.status == SkillMatchStatus.EXACT_MATCH:
            total_credit += 1.0
            exact_count += 1
            evidence.append(f"{item.skill}: Exact match ({item.evidence_source or 'profile'})")
        elif item.status == SkillMatchStatus.ALIAS_MATCH:
            total_credit += 1.0
            alias_count += 1
            evidence.append(f"{item.skill}: Alias match ('{item.candidate_evidence}')")
        elif item.status == SkillMatchStatus.SEMANTICALLY_RELATED:
            total_credit += 0.5
            related_count += 1
            evidence.append(f"{item.skill}: Related technology ('{item.candidate_evidence}')")
        else:
            missing_count += 1
            evidence.append(f"{item.skill}: Missing")

    raw_score = round((total_credit / len(req_items)) * 100.0, 1)
    reason = (
        f"Matched {exact_count + alias_count} exact/alias and {related_count} related "
        f"out of {len(req_items)} required skills ({missing_count} missing)."
    )
    return ComponentAvailability.AVAILABLE, raw_score, evidence, reason


def evaluate_preferred_skills_component(
    skill_matches: list[SkillMatchItem],
    base_weight: float,
) -> tuple[ComponentAvailability, float | None, list[str], str]:
    """Evaluate Preferred Skills dimension."""
    pref_items = [m for m in skill_matches if m.requirement_type == SkillRequirementType.PREFERRED]

    if not pref_items:
        return (
            ComponentAvailability.UNAVAILABLE,
            None,
            [],
            "Job description does not specify preferred/nice-to-have skills.",
        )

    total_credit = 0.0
    evidence: list[str] = []
    matched_count = 0

    for item in pref_items:
        if item.status in (SkillMatchStatus.EXACT_MATCH, SkillMatchStatus.ALIAS_MATCH):
            total_credit += 1.0
            matched_count += 1
            evidence.append(f"{item.skill}: Matched ({item.candidate_evidence or 'exact'})")
        elif item.status == SkillMatchStatus.SEMANTICALLY_RELATED:
            total_credit += 0.5
            matched_count += 1
            evidence.append(f"{item.skill}: Related ('{item.candidate_evidence}')")
        else:
            evidence.append(f"{item.skill}: Missing")

    raw_score = round((total_credit / len(pref_items)) * 100.0, 1)
    reason = f"Matched {matched_count} of {len(pref_items)} preferred skills."
    return ComponentAvailability.AVAILABLE, raw_score, evidence, reason


def evaluate_experience_component(
    experience_match: ExperienceMatchResult,
    base_weight: float,
) -> tuple[ComponentAvailability, float | None, list[str], str]:
    """Evaluate Experience dimension."""
    assessment = experience_match.assessment

    if assessment == ExperienceAssessmentStatus.NOT_REQUIRED:
        return (
            ComponentAvailability.UNAVAILABLE,
            None,
            [experience_match.explanation],
            "Job description does not require minimum professional experience.",
        )

    if assessment == ExperienceAssessmentStatus.INSUFFICIENT_DATA:
        return (
            ComponentAvailability.INSUFFICIENT_DATA,
            None,
            experience_match.missing_information,
            "Candidate experience entries lack dates to verify required duration.",
        )

    # Available calculations
    raw_score: float
    if assessment in (ExperienceAssessmentStatus.EXCEEDS_REQUIREMENT, ExperienceAssessmentStatus.MEETS_REQUIREMENT):
        raw_score = 100.0
    elif assessment == ExperienceAssessmentStatus.PARTIAL:
        req_yrs = experience_match.required_years or 1.0
        prof_yrs = experience_match.professional_years or 0.0
        ratio = min(1.0, prof_yrs / req_yrs)
        base = ratio * 75.0
        # Partial credit for internship and project portfolio
        supp_bonus = min(15.0, (experience_match.internship_years or 0.0) * 5.0 + len(experience_match.project_evidence) * 2.5)
        raw_score = min(85.0, round(base + supp_bonus, 1))
    else:  # BELOW_REQUIREMENT
        if (experience_match.professional_years or 0.0) == 0.0:
            if experience_match.internship_entries or experience_match.project_evidence:
                port_credit = min(30.0, (experience_match.internship_years or 0.0) * 10.0 + len(experience_match.project_evidence) * 5.0)
                raw_score = max(15.0, round(port_credit, 1))
            else:
                raw_score = 0.0
        else:
            raw_score = 0.0

    evidence = [experience_match.explanation] + experience_match.relevant_responsibilities[:3]
    return ComponentAvailability.AVAILABLE, raw_score, evidence, experience_match.explanation


def evaluate_education_component(
    education_match: EducationMatchResult,
    base_weight: float,
) -> tuple[ComponentAvailability, float | None, list[str], str]:
    """Evaluate Education dimension."""
    status = education_match.status

    if status == EducationMatchStatus.NOT_REQUIRED:
        return (
            ComponentAvailability.UNAVAILABLE,
            None,
            [education_match.explanation],
            "Job description does not specify education requirements.",
        )

    if status == EducationMatchStatus.INSUFFICIENT_DATA:
        return (
            ComponentAvailability.INSUFFICIENT_DATA,
            None,
            [education_match.explanation],
            "Candidate education entries lack identifiable degree level.",
        )

    raw_score: float
    if status == EducationMatchStatus.EXACT_MATCH:
        raw_score = 100.0
    elif status == EducationMatchStatus.RELATED_MATCH:
        raw_score = 75.0 if education_match.is_required else 60.0
    else:  # MISSING
        raw_score = 0.0

    return ComponentAvailability.AVAILABLE, raw_score, [education_match.explanation], education_match.explanation


def evaluate_lexical_component(
    candidate_text: str,
    jd_raw_text: str,
    base_weight: float,
) -> tuple[ComponentAvailability, float | None, list[str], str]:
    """Evaluate Lexical Relevance dimension."""
    if not candidate_text or not candidate_text.strip():
        return (
            ComponentAvailability.UNAVAILABLE,
            None,
            [],
            "Insufficient candidate text to compute lexical similarity.",
        )

    score, top_terms = calculate_lexical_similarity(candidate_text, jd_raw_text)
    evidence = [f"Shared terms: {', '.join(top_terms)}"] if top_terms else []
    reason = f"Deterministic lexical surface similarity of {score}% against JD text."
    return ComponentAvailability.AVAILABLE, score, evidence, reason


def classify_score(overall_score: float | None) -> str:
    """Classify match score into standardized product indicators."""
    if overall_score is None:
        return "Not assessable"
    if overall_score >= 80.0:
        return "Strong Match"
    elif overall_score >= 60.0:
        return "Moderate Match"
    elif overall_score >= 40.0:
        return "Partial Match"
    else:
        return "Low Match"


def calculate_match_score(
    parsed_jd: ParsedJobDescription,
    skill_matches: list[SkillMatchItem],
    experience_match: ExperienceMatchResult,
    education_match: EducationMatchResult,
    candidate: CandidateProfile | None = None,
    candidate_text: str | None = None,
    weights: dict[str, float] | None = None,
) -> MatchScoreBreakdown:
    """
    Calculate an explainable, multi-dimensional match score.

    Implements weight normalization when components are unavailable or unassessed.
    """
    cfg_weights = dict(weights) if weights else dict(DEFAULT_WEIGHTS)
    validate_weights(cfg_weights)

    text_to_compare = candidate_text or _build_candidate_full_text(candidate)

    # 1. Evaluate individual components
    components: dict[str, ComponentScore] = {}

    eval_results = {
        "required_skills": evaluate_required_skills_component(
            skill_matches, cfg_weights["required_skills"]
        ),
        "preferred_skills": evaluate_preferred_skills_component(
            skill_matches, cfg_weights["preferred_skills"]
        ),
        "experience": evaluate_experience_component(
            experience_match, cfg_weights["experience"]
        ),
        "education": evaluate_education_component(
            education_match, cfg_weights["education"]
        ),
        "lexical_relevance": evaluate_lexical_component(
            text_to_compare, parsed_jd.raw_text, cfg_weights["lexical_relevance"]
        ),
    }

    # 2. Identify Available Weight Sum for Normalization
    available_weight_sum = sum(
        cfg_weights[cname]
        for cname, (avail, raw_score, _, _) in eval_results.items()
        if avail == ComponentAvailability.AVAILABLE and raw_score is not None
    )

    weight_normalization_applied = 0.0 < available_weight_sum < 0.9999
    total_contribution = 0.0

    # 3. Calculate Normalized Weights and Weighted Contributions
    for cname, (avail, raw_score, evidence, reason) in eval_results.items():
        base_w = cfg_weights[cname]

        if avail == ComponentAvailability.AVAILABLE and raw_score is not None and available_weight_sum > 0.0:
            norm_w = base_w / available_weight_sum
            contribution = raw_score * norm_w
            total_contribution += contribution
            display_norm_w = round(norm_w, 4)
            display_contribution = round(contribution, 2)
        else:
            display_norm_w = 0.0
            display_contribution = 0.0

        components[cname] = ComponentScore(
            component_name=cname,
            availability=avail,
            raw_score=raw_score,
            base_weight=base_w,
            normalized_weight=display_norm_w,
            weighted_contribution=display_contribution,
            evidence=evidence,
            reason=reason,
        )

    # 4. Final Aggregated Score
    if available_weight_sum == 0.0:
        overall_score = None
        classification = "Not assessable"
    else:
        overall_score = min(100.0, max(0.0, round(total_contribution, 1)))
        classification = classify_score(overall_score)

    # 5. Formulate Human-Readable Narrative Explanation
    avail_names = [
        cname.replace("_", " ").title()
        for cname, c in components.items()
        if c.availability == ComponentAvailability.AVAILABLE
    ]
    unavail_names = [
        cname.replace("_", " ").title()
        for cname, c in components.items()
        if c.availability != ComponentAvailability.AVAILABLE
    ]

    unavail_note = (
        f" Unassessed dimensions ({', '.join(unavail_names)}) were safely excluded and weights were re-normalized."
        if weight_normalization_applied
        else ""
    )

    if available_weight_sum == 0.0:
        narrative = "No scoring components were available for evaluation. The match is not assessable."
    else:
        narrative = (
            f"Candidate received an overall match score of {overall_score}% ({classification}) "
            f"evaluated across {len(avail_names)} available dimensions: {', '.join(avail_names)}.{unavail_note}"
        )

    return MatchScoreBreakdown(
        overall_score=overall_score,
        match_classification=classification,
        components=components,
        weight_normalization_applied=weight_normalization_applied,
        explanation=narrative,
    )

