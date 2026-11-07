"""
Actionable Recommendation Engine (Phase 5.5).

Converts verified job-match gaps from Phase 5.1–5.4 into prioritized,
practical learning, project-building, and portfolio improvement recommendations.

Principles:
1. Grounded strictly in JD requirements and candidate evidence gaps.
2. Deterministic, offline, zero external LLMs, zero paid APIs.
3. Deduplicated by requirement to prevent repetitive suggestions.
4. Distinguishes professional employment, internships, and projects.
5. Never suggests fabricating experience or misrepresenting education credentials.
6. Does NOT recommend learning skills that are already adequately matched.
"""

from schemas.matching_schema import (
    ParsedJobDescription,
    SkillMatchItem,
    SkillMatchStatus,
    SkillRequirementType,
    ExperienceMatchResult,
    EducationMatchResult,
    EducationMatchStatus,
    MatchScoreBreakdown,
    RecommendationPriority,
    RecommendationCategory,
    ActionableRecommendation,
)


# Priority numerical weights for deterministic sorting (lower number = higher priority)
PRIORITY_ORDER = {
    RecommendationPriority.HIGH: 0,
    RecommendationPriority.MEDIUM: 1,
    RecommendationPriority.LOW: 2,
}

# Category secondary sort order
CATEGORY_ORDER = {
    RecommendationCategory.REQUIRED_SKILL: 0,
    RecommendationCategory.EDUCATION: 1,
    RecommendationCategory.EXPERIENCE: 2,
    RecommendationCategory.RELATED_SKILL: 3,
    RecommendationCategory.PROJECT: 4,
    RecommendationCategory.PREFERRED_SKILL: 5,
}


def _clean_id_token(token: str) -> str:
    """Normalize a token into a safe deterministic snake_case ID component."""
    return "".join(c if c.isalnum() else "_" for c in token.lower().strip()).strip("_")


def generate_recommendations(
    parsed_jd: ParsedJobDescription,
    matched_skills: list[SkillMatchItem],
    experience_match: ExperienceMatchResult | None = None,
    education_match: EducationMatchResult | None = None,
    score_breakdown: MatchScoreBreakdown | None = None,
) -> list[ActionableRecommendation]:
    """
    Generate prioritized, actionable learning and career recommendations based on match gaps.

    Args:
        parsed_jd: Structured representation of the target job posting.
        matched_skills: Evidence-evaluated skill matching items.
        experience_match: Optional evaluation of professional, internship, and project experience.
        education_match: Optional evaluation of candidate educational qualifications.
        score_breakdown: Optional explainable scoring breakdown.

    Returns:
        List of ActionableRecommendation models sorted by priority and relevance.
    """
    recommendations: list[ActionableRecommendation] = []
    seen_ids: set[str] = set()

    # -------------------------------------------------------------------------
    # 1. Skill Gap Recommendations
    # -------------------------------------------------------------------------
    for item in matched_skills:
        skill_name = item.skill
        clean_token = _clean_id_token(skill_name)

        # RULE: Never recommend learning a skill that is already adequately matched
        if item.status in (SkillMatchStatus.EXACT_MATCH, SkillMatchStatus.ALIAS_MATCH):
            continue

        # Scenario A: Missing Required Skill
        if item.status == SkillMatchStatus.MISSING and item.requirement_type == SkillRequirementType.REQUIRED:
            rec_id = f"rec_req_skill_{clean_token}"
            if rec_id in seen_ids:
                continue
            seen_ids.add(rec_id)

            recommendations.append(
                ActionableRecommendation(
                    recommendation_id=rec_id,
                    category=RecommendationCategory.REQUIRED_SKILL,
                    title=f"Acquire Core Required Skill: {skill_name}",
                    description=(
                        f"'{skill_name}' is a mandatory requirement for this role, but was not "
                        f"detected in your resume or project history."
                    ),
                    priority=RecommendationPriority.HIGH,
                    related_requirement=skill_name,
                    reason="Mandatory technical skill missing from candidate profile.",
                    candidate_evidence=None,
                    suggested_actions=[
                        f"Study foundational concepts, architecture, and production workflows for {skill_name}.",
                        f"Build an end-to-end practical project or service utilizing {skill_name}.",
                        f"Document hands-on implementations in a public repository, and add {skill_name} to your resume only after completing working deliverables.",
                    ],
                    estimated_effort="2-4 weeks",
                    source_component="skill",
                )
            )

        # Scenario B: Semantically Related Required Skill (Bridge Gap)
        elif item.status == SkillMatchStatus.SEMANTICALLY_RELATED and item.requirement_type == SkillRequirementType.REQUIRED:
            rec_id = f"rec_related_skill_{clean_token}"
            if rec_id in seen_ids:
                continue
            seen_ids.add(rec_id)

            cand_ev = item.candidate_evidence or "a related technology"
            recommendations.append(
                ActionableRecommendation(
                    recommendation_id=rec_id,
                    category=RecommendationCategory.RELATED_SKILL,
                    title=f"Bridge Skill Gap from {cand_ev} to {skill_name}",
                    description=(
                        f"Your profile demonstrates familiarity with {cand_ev}, which is conceptually "
                        f"related to required {skill_name}. However, {skill_name} is a distinct required tool "
                        f"that requires hands-on demonstration."
                    ),
                    priority=RecommendationPriority.MEDIUM,
                    related_requirement=skill_name,
                    reason=f"Candidate demonstrates {cand_ev} but lacks direct evidence for required {skill_name}.",
                    candidate_evidence=cand_ev,
                    suggested_actions=[
                        f"Study the architectural differences and core paradigms separating {cand_ev} and {skill_name}.",
                        f"Build a practical, deployed project or microservice implementing {skill_name} to establish hands-on proficiency.",
                        f"Only after building verifiable project evidence, document your hands-on competency with {skill_name} in your technical profile.",
                    ],
                    estimated_effort="1-2 weeks",
                    source_component="skill",
                )
            )

        # Scenario C: Missing Preferred Skill
        elif item.status == SkillMatchStatus.MISSING and item.requirement_type == SkillRequirementType.PREFERRED:
            rec_id = f"rec_pref_skill_{clean_token}"
            if rec_id in seen_ids:
                continue
            seen_ids.add(rec_id)

            recommendations.append(
                ActionableRecommendation(
                    recommendation_id=rec_id,
                    category=RecommendationCategory.PREFERRED_SKILL,
                    title=f"Learn Preferred Technology: {skill_name}",
                    description=(
                        f"'{skill_name}' is listed as a preferred qualification. Developing practical project "
                        f"implementations with {skill_name} will establish verifiable evidence for this role."
                    ),
                    priority=RecommendationPriority.LOW,
                    related_requirement=skill_name,
                    reason="Preferred skill not currently evidenced in candidate profile.",
                    candidate_evidence=None,
                    suggested_actions=[
                        f"Review official documentation and core design patterns for {skill_name}.",
                        f"Build a practical prototype or sandbox project demonstrating hands-on usage of {skill_name}.",
                        f"Include {skill_name} in your technical profile only after completing functional project deliverables.",
                    ],
                    estimated_effort="1-2 weeks",
                    source_component="skill",
                )
            )

        # Scenario D: Semantically Related Preferred Skill
        elif item.status == SkillMatchStatus.SEMANTICALLY_RELATED and item.requirement_type == SkillRequirementType.PREFERRED:
            rec_id = f"rec_related_pref_skill_{clean_token}"
            if rec_id in seen_ids:
                continue
            seen_ids.add(rec_id)

            cand_ev = item.candidate_evidence or "a related tool"
            recommendations.append(
                ActionableRecommendation(
                    recommendation_id=rec_id,
                    category=RecommendationCategory.PREFERRED_SKILL,
                    title=f"Bridge Experience from {cand_ev} to Preferred {skill_name}",
                    description=(
                        f"You have experience with {cand_ev}, which relates to preferred {skill_name}. "
                        f"Acquiring hands-on practice with {skill_name} will strengthen your profile."
                    ),
                    priority=RecommendationPriority.LOW,
                    related_requirement=skill_name,
                    reason=f"Candidate has related skill {cand_ev} for preferred skill {skill_name}.",
                    candidate_evidence=cand_ev,
                    suggested_actions=[
                        f"Explore tutorials and core APIs for {skill_name} leveraging your familiarity with {cand_ev}.",
                        f"Implement a working prototype with {skill_name} to gain demonstrable experience before listing it on your profile.",
                    ],
                    estimated_effort="3-5 days",
                    source_component="skill",
                )
            )

    # -------------------------------------------------------------------------
    # 2. Experience Recommendations
    # -------------------------------------------------------------------------
    if experience_match is not None:
        prof_years = experience_match.professional_years or 0.0
        intern_years = experience_match.internship_years or 0.0
        req_years = experience_match.required_years
        project_count = len(experience_match.project_evidence)

        # Gap 1: Insufficient professional employment duration
        if req_years is not None and req_years > 0:
            if prof_years < req_years:
                gap = round(req_years - prof_years, 1)
                rec_id = "rec_exp_tenure_gap"
                if rec_id not in seen_ids:
                    seen_ids.add(rec_id)

                    if intern_years > 0:
                        desc = (
                            f"The position requires {req_years} years of professional employment. "
                            f"Your profile reflects {prof_years} years of full-time professional experience "
                            f"and {intern_years} years of internship experience. While internships demonstrate "
                            f"applied ability, full commercial tenure falls below the stated threshold."
                        )
                        actions = [
                            f"Highlight substantial engineering accomplishments and autonomous delivery during your {intern_years} years of internship experience.",
                            "Develop production-grade, deployed portfolio systems showcasing scalability, monitoring, and architecture.",
                            "Target junior, associate, or rotational software engineering roles to accumulate commercial tenure.",
                        ]
                    else:
                        desc = (
                            f"The position requires {req_years} years of professional work experience, "
                            f"while your profile reflects {prof_years} years."
                        )
                        actions = [
                            "Build end-to-end production systems with automated testing, CI/CD, and cloud deployment to demonstrate practical engineering maturity.",
                            "Pursue entry-level, junior, or contract software engineering positions to build verified professional tenure.",
                            "Contribute to active open-source repositories to gain documented collaborative team experience.",
                        ]

                    prio = RecommendationPriority.HIGH if gap >= 2.0 else RecommendationPriority.MEDIUM
                    recommendations.append(
                        ActionableRecommendation(
                            recommendation_id=rec_id,
                            category=RecommendationCategory.EXPERIENCE,
                            title=f"Address Professional Experience Gap ({prof_years} yrs vs {req_years} yrs required)",
                            description=desc,
                            priority=prio,
                            related_requirement=f"{req_years} years experience",
                            reason=f"Candidate professional tenure ({prof_years} years) is below required {req_years} years.",
                            candidate_evidence=f"{prof_years} yrs professional, {intern_years} yrs internship" if intern_years > 0 else f"{prof_years} yrs",
                            suggested_actions=actions,
                            estimated_effort="Ongoing commercial tenure",
                            source_component="experience",
                        )
                    )

        # Gap 2: Missing practical project evidence
        if project_count == 0:
            rec_id = "rec_exp_missing_projects"
            if rec_id not in seen_ids:
                seen_ids.add(rec_id)
                prio = RecommendationPriority.HIGH if prof_years == 0 else RecommendationPriority.MEDIUM
                recommendations.append(
                    ActionableRecommendation(
                        recommendation_id=rec_id,
                        category=RecommendationCategory.PROJECT,
                        title="Build and Document Production-Grade Portfolio Projects",
                        description=(
                            "No project entries were detected in your resume profile. Portfolio projects "
                            "provide critical evidence of hands-on design, coding, and deployment capability."
                        ),
                        priority=prio,
                        related_requirement="Practical project demonstrations",
                        reason="Resume lacks dedicated project entries validating technical proficiency.",
                        candidate_evidence=None,
                        suggested_actions=[
                            "Design and build 1-2 full-stack or backend projects matching the target domain of this role.",
                            "Publish clean, documented code on GitHub with comprehensive unit tests and automated CI/CD workflows.",
                            "Deploy live demonstrations or APIs with clear README documentation and architecture diagrams.",
                        ],
                        estimated_effort="2-4 weeks per project",
                        source_component="experience",
                    )
                )

        # Gap 3: Missing information (e.g. missing dates)
        if experience_match.missing_information:
            rec_id = "rec_exp_missing_dates"
            if rec_id not in seen_ids:
                seen_ids.add(rec_id)
                recommendations.append(
                    ActionableRecommendation(
                        recommendation_id=rec_id,
                        category=RecommendationCategory.EXPERIENCE,
                        title="Clarify Employment Dates and Durations",
                        description=(
                            "Some experience entries lack clear start or end dates, which prevents calculating "
                            "your full verifiable commercial tenure."
                        ),
                        priority=RecommendationPriority.MEDIUM,
                        related_requirement="Employment dates",
                        reason="Missing or ambiguous employment dates in experience entries.",
                        candidate_evidence="; ".join(experience_match.missing_information[:2]),
                        suggested_actions=[
                            "Add clear 'Month Year – Month Year' (or 'Present') date ranges to each work experience entry.",
                            "Ensure internship roles explicitly include the title 'Intern' or 'Internship' and respective dates.",
                        ],
                        estimated_effort="1-2 hours",
                        source_component="experience",
                    )
                )

        # Gap 4: Low responsibility alignment
        if len(experience_match.relevant_responsibilities) == 0 and parsed_jd.responsibilities:
            rec_id = "rec_exp_responsibility_alignment"
            if rec_id not in seen_ids:
                seen_ids.add(rec_id)
                sample_resp = parsed_jd.responsibilities[0] if parsed_jd.responsibilities else "Core role duties"
                recommendations.append(
                    ActionableRecommendation(
                        recommendation_id=rec_id,
                        category=RecommendationCategory.EXPERIENCE,
                        title="Align Work Experience Bullets with Role Responsibilities",
                        description=(
                            f"Your work experience does not explicitly reflect core role responsibilities "
                            f"(such as '{sample_resp}'). Tailoring your descriptions to emphasize relevant "
                            f"impact will improve match alignment."
                        ),
                        priority=RecommendationPriority.MEDIUM,
                        related_requirement="Role responsibilities",
                        reason="No relevant responsibilities detected matching the target job description.",
                        candidate_evidence=None,
                        suggested_actions=[
                            "Rephrase experience bullet points using impact-driven metrics (e.g. 'Improved X by Y% using Z').",
                            "Highlight system architecture, collaboration, and delivery duties aligned with target responsibilities.",
                        ],
                        estimated_effort="1-3 days",
                        source_component="experience",
                    )
                )

    # -------------------------------------------------------------------------
    # 3. Education Recommendations
    # -------------------------------------------------------------------------
    if education_match is not None:
        req_deg = education_match.required_degree or "Degree"
        fields_str = ", ".join(education_match.required_fields) if education_match.required_fields else "Relevant Field"

        # Scenario A: Missing Degree
        if education_match.status == EducationMatchStatus.MISSING:
            rec_id = "rec_edu_missing_degree"
            if rec_id not in seen_ids:
                seen_ids.add(rec_id)

                if education_match.is_required:
                    # Mandatory requirement missing
                    recommendations.append(
                        ActionableRecommendation(
                            recommendation_id=rec_id,
                            category=RecommendationCategory.EDUCATION,
                            title=f"Address Mandatory Education Requirement: {req_deg} in {fields_str}",
                            description=(
                                f"The position specifies a mandatory {req_deg} in {fields_str}. "
                                f"Candidate profile reflects {education_match.candidate_degree or 'no recognized degree entry'}."
                            ),
                            priority=RecommendationPriority.HIGH,
                            related_requirement=f"{req_deg} in {fields_str}",
                            reason="Mandatory educational qualification not satisfied by candidate profile.",
                            candidate_evidence=education_match.candidate_degree,
                            suggested_actions=[
                                "Investigate if the hiring team accepts verified commercial engineering experience in lieu of formal degree.",
                                "Pursue accredited degree completion, post-graduate diplomas, or recognized formal certifications.",
                                "Compensate by highlighting rigorous technical achievements, open-source codebases, and production deployments.",
                            ],
                            estimated_effort="Long-term educational pathway",
                            source_component="education",
                        )
                    )
                else:
                    # Preferred qualification gap
                    recommendations.append(
                        ActionableRecommendation(
                            recommendation_id=rec_id,
                            category=RecommendationCategory.EDUCATION,
                            title=f"Consider Preferred Education Credential: {req_deg}",
                            description=(
                                f"A {req_deg} in {fields_str} is preferred by the employer. While not mandatory, "
                                f"relevant credentials or university-level certificates can enhance your competitiveness."
                            ),
                            priority=RecommendationPriority.LOW,
                            related_requirement=f"Preferred {req_deg}",
                            reason="Preferred educational qualification not found in candidate profile.",
                            candidate_evidence=education_match.candidate_degree,
                            suggested_actions=[
                                f"Complete university-affiliated certificate programs or accredited coursework in {fields_str}.",
                                "Focus on high-impact practical projects and demonstrable domain depth to offset preferred academic credentials.",
                            ],
                            estimated_effort="3-6 months",
                            source_component="education",
                        )
                    )

        # Scenario B: Related Degree with Field of Study Mismatch
        elif (
            education_match.status == EducationMatchStatus.RELATED_MATCH
            and not education_match.field_match
            and education_match.required_fields
        ):
            rec_id = "rec_edu_field_alignment"
            if rec_id not in seen_ids:
                seen_ids.add(rec_id)
                cand_field = education_match.candidate_field or "Current Major"
                recommendations.append(
                    ActionableRecommendation(
                        recommendation_id=rec_id,
                        category=RecommendationCategory.EDUCATION,
                        title=f"Bridge Academic Discipline Gap ({cand_field} to {fields_str})",
                        description=(
                            f"Your profile reflects a {education_match.candidate_degree or 'degree'} in {cand_field}, "
                            f"whereas the job requests {fields_str}."
                        ),
                        priority=RecommendationPriority.LOW,
                        related_requirement=f"Discipline: {fields_str}",
                        reason=f"Candidate degree meets level requirement but discipline ({cand_field}) differs from target fields.",
                        candidate_evidence=f"{education_match.candidate_degree} in {cand_field}",
                        suggested_actions=[
                            "Highlight quantitative, analytical, or algorithmic coursework completed during your studies.",
                            "Obtain recognized technical certifications to demonstrate formal computer science rigor.",
                        ],
                        estimated_effort="1-3 months",
                        source_component="education",
                    )
                )

    # -------------------------------------------------------------------------
    # 4. Deterministic Priority Ranking & Sorting
    # -------------------------------------------------------------------------
    # Sort criteria:
    # 1. Priority (HIGH=0, MEDIUM=1, LOW=2)
    # 2. Category order (REQUIRED_SKILL, EDUCATION, EXPERIENCE, RELATED_SKILL, PROJECT, PREFERRED_SKILL)
    # 3. Recommendation Title (alphabetical tie-breaker)
    recommendations.sort(
        key=lambda r: (
            PRIORITY_ORDER.get(r.priority, 99),
            CATEGORY_ORDER.get(r.category, 99),
            r.title,
        )
    )

    return recommendations
