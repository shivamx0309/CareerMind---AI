"""
Skill Normalization and Matching Engine for CareerMind AI (Phase 5.2).

Compares candidate profile skills and experience against job description requirements.
Classifies each target JD skill into one of four distinct states:
1. exact_match: Candidate profile contains the exact canonical skill (match_confidence = 1.0)
2. alias_match: Candidate profile contains a canonical alias of the skill (match_confidence = 1.0)
3. semantically_related: Candidate lacks the skill but possesses a closely related technology in the same domain cluster (match_confidence = 0.6)
4. missing: Candidate has no direct, alias, or related evidence (match_confidence = 0.0)

Evidence sources scanned:
- technical_skills (categorized competencies)
- experience (roles, responsibilities, and technologies used)
- projects (portfolio projects, descriptions, and technologies)
- certifications & achievements (credential names and milestones)

Rules:
- Reuses existing SKILL_TAXONOMY and CANONICAL_ALIASES from resume_engine.
- Semantically related skills are never counted as exact matches.
- Missing skills remain missing unless there is defensible evidence.
- Double-counting across multiple evidence sources is strictly prevented.
"""

import re
from schemas.candidate_schema import CandidateProfile
from schemas.matching_schema import (
    ParsedJobDescription,
    SkillMatchItem,
    SkillRequirementType,
    SkillMatchStatus,
)
from resume_engine.skills_parser import (
    SKILL_TAXONOMY,
    CANONICAL_ALIASES,
    resolve_skill_alias,
)


# ============================================================================
# Defensible Semantic Technology Clusters
# ============================================================================
# Groups technologies that are closely related within the same technical domain.
# Used exclusively for classifying "semantically_related" when an exact or alias match is absent.

RELATED_SKILL_CLUSTERS: list[tuple[str, set[str]]] = [
    ("Python Web Frameworks", {"FastAPI", "Django", "Flask", "Tornado"}),
    ("Frontend UI Frameworks", {"React", "Vue.js", "Angular", "Svelte"}),
    ("Full-Stack Frameworks", {"Next.js", "Remix", "Nuxt.js", "SvelteKit"}),
    ("CSS Frameworks & Preprocessors", {"Tailwind CSS", "Bootstrap", "Sass", "CSS3"}),
    ("Relational SQL Databases", {"PostgreSQL", "MySQL", "MariaDB", "SQLite", "Oracle"}),
    ("NoSQL & Document Databases", {"MongoDB", "Cassandra", "DynamoDB", "Firestore", "Firebase"}),
    ("In-Memory Caching & Stores", {"Redis", "Memcached"}),
    ("Containerization & Orchestration", {"Docker", "Kubernetes"}),
    ("Cloud Infrastructure", {"AWS", "Azure", "GCP"}),
    ("Deep Learning Frameworks", {"PyTorch", "TensorFlow", "Keras"}),
    ("Data Analysis Libraries", {"Pandas", "NumPy", "Data Analytics"}),
    ("CI/CD Automation", {"GitHub Actions", "GitLab CI", "Jenkins"}),
    ("API Architectures", {"REST API", "GraphQL", "gRPC"}),
    ("State Management", {"Redux", "Zustand", "MobX"}),
    ("Node.js Frameworks", {"Express", "NestJS"}),
    ("Testing & QA Tools", {"Postman", "Selenium", "Jest", "Pytest", "Web Testing", "Unit Testing"}),
]


class CandidateEvidenceRecord:
    """Internal representation of a piece of candidate skill evidence."""

    def __init__(
        self,
        canonical_name: str,
        original_token: str,
        source_type: str,
        context: str,
    ):
        self.canonical_name = canonical_name
        self.original_token = original_token
        self.source_type = source_type
        self.context = context


def extract_candidate_skill_evidence(
    candidate: CandidateProfile,
) -> dict[str, list[CandidateEvidenceRecord]]:
    """
    Index all skill evidence from a CandidateProfile across all 5 sections:
    - technical_skills
    - experience
    - projects
    - certifications
    - achievements

    Returns mapping:
        canonical_skill_lower -> list[CandidateEvidenceRecord]
    """
    evidence_index: dict[str, list[CandidateEvidenceRecord]] = {}

    def _add_evidence(canonical: str, original: str, source: str, context: str):
        key = canonical.lower()
        if key not in evidence_index:
            evidence_index[key] = []
        # Avoid duplicate records for identical original token from same source
        if not any(e.source_type == source and e.original_token.lower() == original.lower() for e in evidence_index[key]):
            evidence_index[key].append(
                CandidateEvidenceRecord(
                    canonical_name=canonical,
                    original_token=original,
                    source_type=source,
                    context=context,
                )
            )

    # 1. Technical Skills
    tech_skills = candidate.technical_skills
    if tech_skills:
        for cat_name in (
            "programming_languages",
            "frontend",
            "backend",
            "databases",
            "data_analytics",
            "machine_learning",
            "deep_learning",
            "cloud_devops",
            "tools",
            "other",
        ):
            skill_list = getattr(tech_skills, cat_name, []) or []
            for skill_str in skill_list:
                clean = skill_str.strip()
                if not clean:
                    continue
                # Canonicalize
                alias_res = resolve_skill_alias(clean)
                canon = alias_res[0] if alias_res else clean
                _add_evidence(
                    canonical=canon,
                    original=clean,
                    source="technical_skills",
                    context=f"Declared under technical_skills ({cat_name})",
                )

    # 2. Experience
    for exp in candidate.experience or []:
        role_label = f"{exp.job_title or 'Role'} at {exp.company or 'Company'}"

        # Explicit technologies list
        for tech in exp.technologies or []:
            clean = tech.strip()
            if not clean:
                continue
            alias_res = resolve_skill_alias(clean)
            canon = alias_res[0] if alias_res else clean
            _add_evidence(
                canonical=canon,
                original=clean,
                source="experience",
                context=f"Listed in technologies for {role_label}",
            )

        # Experience description scanning
        if exp.description:
            desc_lines = exp.description.splitlines()
            for line in desc_lines:
                clean_line = line.strip()
                if not clean_line:
                    continue
                for _cat, skills in SKILL_TAXONOMY.items():
                    for canonical_name, pattern in skills:
                        if canonical_name == "Regression" and re.search(r"\bregression\s+testing\b", clean_line, re.I):
                            continue
                        m = re.search(pattern, clean_line, re.IGNORECASE)
                        if m:
                            _add_evidence(
                                canonical=canonical_name,
                                original=m.group(0),
                                source="experience",
                                context=f"Used in {role_label}: '{clean_line}'",
                            )

    # 3. Projects
    for proj in candidate.projects or []:
        proj_name = proj.project_name or "Project"

        # Explicit technologies list
        for tech in proj.technologies or []:
            clean = tech.strip()
            if not clean:
                continue
            alias_res = resolve_skill_alias(clean)
            canon = alias_res[0] if alias_res else clean
            _add_evidence(
                canonical=canon,
                original=clean,
                source="projects",
                context=f"Listed in technologies for project '{proj_name}'",
            )

        # Project description scanning
        if proj.description:
            desc_lines = proj.description.splitlines()
            for line in desc_lines:
                clean_line = line.strip()
                if not clean_line:
                    continue
                for _cat, skills in SKILL_TAXONOMY.items():
                    for canonical_name, pattern in skills:
                        if canonical_name == "Regression" and re.search(r"\bregression\s+testing\b", clean_line, re.I):
                            continue
                        m = re.search(pattern, clean_line, re.IGNORECASE)
                        if m:
                            _add_evidence(
                                canonical=canonical_name,
                                original=m.group(0),
                                source="projects",
                                context=f"Used in project '{proj_name}': '{clean_line}'",
                            )

    # 4. Certifications
    for cert in candidate.certifications or []:
        cname = cert.certification_name or ""
        if cname:
            for _cat, skills in SKILL_TAXONOMY.items():
                for canonical_name, pattern in skills:
                    m = re.search(pattern, cname, re.IGNORECASE)
                    if m:
                        _add_evidence(
                            canonical=canonical_name,
                            original=m.group(0),
                            source="certifications",
                            context=f"Found in certification '{cname}'",
                        )

    # 5. Achievements
    for ach in candidate.achievements or []:
        atitle = ach.title or ""
        if atitle:
            for _cat, skills in SKILL_TAXONOMY.items():
                for canonical_name, pattern in skills:
                    m = re.search(pattern, atitle, re.IGNORECASE)
                    if m:
                        _add_evidence(
                            canonical=canonical_name,
                            original=m.group(0),
                            source="achievements",
                            context=f"Found in achievement '{atitle}'",
                        )

    return evidence_index


def find_related_skill(
    target_canonical: str,
    evidence_index: dict[str, list[CandidateEvidenceRecord]],
) -> tuple[str, CandidateEvidenceRecord] | None:
    """
    Search for a candidate skill in the same technology cluster as target_canonical.

    Returns:
        tuple of (cluster_name, CandidateEvidenceRecord) or None.
    """
    target_lower = target_canonical.lower()

    for cluster_name, cluster_skills in RELATED_SKILL_CLUSTERS:
        # Check if target skill is a member of this cluster
        cluster_lower_map = {s.lower(): s for s in cluster_skills}
        if target_lower in cluster_lower_map:
            # Check candidate evidence for any other skill in this cluster
            for cand_skill_lower, records in evidence_index.items():
                if cand_skill_lower != target_lower and cand_skill_lower in cluster_lower_map:
                    if records:
                        return cluster_name, records[0]

    return None


def match_single_skill(
    skill_name: str,
    requirement_type: SkillRequirementType,
    evidence_index: dict[str, list[CandidateEvidenceRecord]],
    original_jd_phrase: str | None = None,
) -> SkillMatchItem:
    """
    Evaluate a single JD skill against candidate evidence.

    Determines exact_match, alias_match, semantically_related, or missing.
    """
    # Canonicalize the target skill name
    target_clean = skill_name.strip()
    target_canonical = CANONICAL_ALIASES.get(target_clean.lower(), target_clean)
    target_key = target_canonical.lower()

    records = evidence_index.get(target_key, [])

    if records:
        # Select best evidence source prioritizing technical_skills > experience > projects > certifications > achievements
        source_priority = {
            "technical_skills": 1,
            "experience": 2,
            "projects": 3,
            "certifications": 4,
            "achievements": 5,
        }
        sorted_records = sorted(
            records,
            key=lambda r: source_priority.get(r.source_type, 99)
        )
        primary_record = sorted_records[0]

        # Distinguish exact_match vs alias_match
        is_exact = any(r.original_token.lower() == target_canonical.lower() for r in records)

        if is_exact:
            status = SkillMatchStatus.EXACT_MATCH
            evidence_text = primary_record.original_token
        else:
            status = SkillMatchStatus.ALIAS_MATCH
            evidence_text = primary_record.original_token

        # Consolidate sources without duplicating
        unique_sources = []
        for r in sorted_records:
            if r.source_type not in unique_sources:
                unique_sources.append(r.source_type)
        sources_summary = ", ".join(unique_sources)

        return SkillMatchItem(
            skill=target_canonical,
            requirement_type=requirement_type,
            status=status,
            candidate_evidence=evidence_text,
            evidence_source=sources_summary,
            match_confidence=1.0,
            original_jd_phrase=original_jd_phrase,
        )

    # Check for semantically related skill
    related = find_related_skill(target_canonical, evidence_index)
    if related:
        cluster_name, rel_record = related
        return SkillMatchItem(
            skill=target_canonical,
            requirement_type=requirement_type,
            status=SkillMatchStatus.SEMANTICALLY_RELATED,
            candidate_evidence=f"{rel_record.original_token} ({cluster_name})",
            evidence_source=rel_record.source_type,
            match_confidence=0.6,
            original_jd_phrase=original_jd_phrase,
        )

    # Missing skill
    return SkillMatchItem(
        skill=target_canonical,
        requirement_type=requirement_type,
        status=SkillMatchStatus.MISSING,
        candidate_evidence=None,
        evidence_source=None,
        match_confidence=0.0,
        original_jd_phrase=original_jd_phrase,
    )


def match_candidate_skills(
    candidate: CandidateProfile,
    parsed_jd: ParsedJobDescription,
) -> tuple[list[SkillMatchItem], list[str], list[str]]:
    """
    Match candidate profile against required and preferred skills from parsed JD.

    Returns:
        tuple of:
        - matched_items: list[SkillMatchItem] for every JD skill
        - missing_required: list[str] of missing required skill names
        - missing_preferred: list[str] of missing preferred skill names
    """
    # 1. Index all candidate skill evidence
    evidence_index = extract_candidate_skill_evidence(candidate)

    match_items: list[SkillMatchItem] = []
    missing_required: list[str] = []
    missing_preferred: list[str] = []

    seen_skills: set[str] = set()

    # 2. Evaluate Required Skills
    for skill in parsed_jd.required_skills:
        skill_clean = skill.strip()
        if not skill_clean or skill_clean.lower() in seen_skills:
            continue
        seen_skills.add(skill_clean.lower())

        jd_phrase = parsed_jd.skill_evidence.get(skill_clean)
        item = match_single_skill(
            skill_name=skill_clean,
            requirement_type=SkillRequirementType.REQUIRED,
            evidence_index=evidence_index,
            original_jd_phrase=jd_phrase,
        )
        match_items.append(item)
        if item.status == SkillMatchStatus.MISSING:
            missing_required.append(item.skill)

    # 3. Evaluate Preferred Skills
    for skill in parsed_jd.preferred_skills:
        skill_clean = skill.strip()
        if not skill_clean or skill_clean.lower() in seen_skills:
            continue
        seen_skills.add(skill_clean.lower())

        jd_phrase = parsed_jd.skill_evidence.get(skill_clean)
        item = match_single_skill(
            skill_name=skill_clean,
            requirement_type=SkillRequirementType.PREFERRED,
            evidence_index=evidence_index,
            original_jd_phrase=jd_phrase,
        )
        match_items.append(item)
        if item.status == SkillMatchStatus.MISSING:
            missing_preferred.append(item.skill)

    return match_items, missing_required, missing_preferred

