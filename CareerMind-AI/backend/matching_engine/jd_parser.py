"""
Job Description Parsing Engine for CareerMind AI (Phase 5).

Extracts structured job requirements from raw job description text:
- Job title, company, location (explicit or heuristic extraction)
- Mandatory / Required technical skills with verbatim evidence
- Preferred / Nice-to-have technical skills with verbatim evidence
- Experience requirements (minimum years, range, seniority level, required vs preferred)
- Education requirements (degree level, fields of study, required vs preferred)
- Core responsibilities and key technical keywords

Reuses canonical skill definitions and alias resolution from `resume_engine.skills_parser`
to guarantee zero dictionary fragmentation across the system.
"""

import re
from schemas.matching_schema import (
    ParsedJobDescription,
    ExperienceRequirement,
    EducationRequirement,
)
from resume_engine.skills_parser import (
    SKILL_TAXONOMY,
    CANONICAL_ALIASES,
)


# ============================================================================
# Section Heading Regular Expressions
# ============================================================================

REQUIRED_HEADINGS = re.compile(
    r"^(?:(?:minimum|basic|core|mandatory)\s+qualifications|(?:job\s+)?requirements|what\s+you(?:'ll|\s+will)\s+need|what\s+we(?:'re|\s+are)\s+looking\s+for|what\s+you\s+bring|required\s+(?:skills|qualifications|experience)|must\s+haves?|must-haves?|skills\s+(?:required|and\s+qualifications)|qualifications\s+required)[\s:]*$",
    re.IGNORECASE,
)

PREFERRED_HEADINGS = re.compile(
    r"^(?:preferred\s+(?:qualifications|skills|experience)|nice\s+to\s+haves?|nice-to-haves?|good\s+to\s+have|bonus\s+(?:points?|qualifications)|plus\s+points?|desired\s+(?:skills|qualifications)|additional\s+qualifications|preferred\s+requirements|bonus)[\s:]*$",
    re.IGNORECASE,
)

RESPONSIBILITIES_HEADINGS = re.compile(
    r"^(?:responsibilities|key\s+responsibilities|role\s+responsibilities|what\s+you(?:'ll|\s+will)\s+do|the\s+role|duties|core\s+responsibilities|what\s+you\s+will\s+be\s+doing|your\s+role)[\s:]*$",
    re.IGNORECASE,
)

OVERVIEW_HEADINGS = re.compile(
    r"^(?:about\s+(?:the\s+role|the\s+job|us|the\s+company)|job\s+(?:summary|overview|description)|who\s+we\s+are|company\s+overview|position\s+overview)[\s:]*$",
    re.IGNORECASE,
)


# ============================================================================
# Experience & Seniority Regular Expressions
# ============================================================================

EXP_RANGE_REGEX = re.compile(
    r"\b(?:at\s+least|minimum(?:\s+of)?\s*)?(\d+(?:\.\d+)?)\s*(?:\+)?\s*(?:(?:to|-)\s*(\d+(?:\.\d+)?))?\s*(?:years?|yrs?)(?:\s*of)?(?:\s+[a-zA-Z\-_/]+){0,4}\s*experience\b",
    re.IGNORECASE,
)

EXP_PLUS_REGEX = re.compile(
    r"\b(\d+(?:\.\d+)?)\+\s*(?:years?|yrs?)(?:\s*of)?\s*(?:experience|exp)?\b",
    re.IGNORECASE,
)

LEVEL_PATTERNS = [
    (r"\b(?:principal|staff|lead\s+(?:engineer|developer|architect)|tech\s+lead|team\s+lead|director)\b", "Lead / Principal"),
    (r"\b(?:senior|sr\.?)\b", "Senior"),
    (r"\b(?:mid[\s-]*level|intermediate)\b", "Mid-level"),
    (r"\b(?:junior|jr\.?|associate|entry[\s-]*level|new\s+grad(?:uate)?|fresher)\b", "Entry-level"),
    (r"\bintern(?:ship)?\b", "Internship"),
]

PREFERRED_CUE_REGEX = re.compile(
    r"\b(?:preferred|nice\s+to\s+have|bonus|plus|desired|optional|a\s+plus)\b",
    re.IGNORECASE,
)

REQUIRED_CUE_REGEX = re.compile(
    r"\b(?:must\s+have|required|mandatory|essential|proficiency\s+in|hands-on\s+experience|solid\s+understanding)\b",
    re.IGNORECASE,
)


# ============================================================================
# Education Regular Expressions
# ============================================================================

DEGREE_PATTERNS = [
    (r"\b(?:ph\.?d|doctorate|doctoral)\b", "PhD"),
    (r"\b(?:master(?:'s)?|ms|m\.s\.?|m\.tech|msc|m\.sc\.?|post[\s-]*graduate)\b", "Master"),
    (r"\b(?:bachelor(?:'s)?|bs|b\.s\.?|b\.tech|b\.e\.?|bsc|b\.sc\.?|undergraduate)\b", "Bachelor"),
    (r"\b(?:associate(?:'s)?\s+degree|diploma)\b", "Associate"),
]

FIELDS_OF_STUDY_PATTERNS = [
    (r"computer\s+science", "Computer Science"),
    (r"software\s+engineering", "Software Engineering"),
    (r"information\s+technology", "Information Technology"),
    (r"(?:electrical|electronics)\s+engineering", "Electrical Engineering"),
    (r"data\s+science", "Data Science"),
    (r"mathematics|math", "Mathematics"),
    (r"statistics|stats", "Statistics"),
    (r"artificial\s+intelligence|machine\s+learning", "Artificial Intelligence"),
]


# ============================================================================
# Title & Entity Patterns
# ============================================================================

KNOWN_TITLES_REGEX = re.compile(
    r"\b(?:software\s+(?:development\s+)?engineer|full[\s-]*stack\s+(?:engineer|developer)|frontend\s+(?:engineer|developer)|backend\s+(?:engineer|developer)|data\s+engineer|data\s+scientist|machine\s+learning\s+engineer|ml\s+engineer|devops\s+engineer|cloud\s+architect|qa\s+(?:engineer|lead|automation\s+engineer)|product\s+manager|solutions\s+architect|mobile\s+developer|ios\s+developer|android\s+developer)\b",
    re.IGNORECASE,
)

LOCATION_TAG_REGEX = re.compile(
    r"^(?:remote|hybrid|on-site|onsite)$|^[A-Za-z\s.-]+,\s*[A-Za-z\s.-]+$",
    re.IGNORECASE,
)

DOMAIN_KEYWORDS = [
    "Microservices",
    "System Design",
    "Distributed Systems",
    "CI/CD",
    "Cloud Computing",
    "Scalability",
    "API Design",
    "Code Review",
    "Automated Testing",
    "Agile",
    "Scrum",
    "High Availability",
    "Performance Optimization",
    "Security",
    "DevOps",
]


# ============================================================================
# Section Segmentation Helper
# ============================================================================

def segment_jd_sections(text: str) -> dict[str, list[str]]:
    """
    Segment job description text into semantic sections.

    Returns dict mapping section keys:
    - 'header': Title and top metadata
    - 'overview': Role summary / company info
    - 'responsibilities': Role duties
    - 'required': Minimum / required qualifications
    - 'preferred': Nice-to-have / bonus qualifications
    - 'general': Unclassified content
    """
    sections: dict[str, list[str]] = {
        "header": [],
        "overview": [],
        "responsibilities": [],
        "required": [],
        "preferred": [],
        "general": [],
    }

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return sections

    has_explicit_sections = any(
        REQUIRED_HEADINGS.match(line)
        or PREFERRED_HEADINGS.match(line)
        or RESPONSIBILITIES_HEADINGS.match(line)
        or OVERVIEW_HEADINGS.match(line)
        for line in lines
    )

    current_section = "header"
    header_count = 0

    for line in lines:
        # Check for explicit section headers
        if REQUIRED_HEADINGS.match(line):
            current_section = "required"
            continue
        elif PREFERRED_HEADINGS.match(line):
            current_section = "preferred"
            continue
        elif RESPONSIBILITIES_HEADINGS.match(line):
            current_section = "responsibilities"
            continue
        elif OVERVIEW_HEADINGS.match(line):
            current_section = "overview"
            continue

        if current_section == "header":
            header_count += 1
            # If explicit headings exist, top 3 lines can be header
            if has_explicit_sections and header_count > 3:
                current_section = "general"
            elif not has_explicit_sections:
                # If no headings exist, put non-metadata lines into general
                is_meta = any(
                    line.lower().startswith(prefix)
                    for prefix in ("job title:", "company:", "location:", "position:")
                )
                if not is_meta:
                    current_section = "general"

        sections[current_section].append(line)

    return sections


# ============================================================================
# Skill Extraction Helper
# ============================================================================

def resolve_known_skill(raw_token: str) -> str | None:
    """
    Resolve a token strictly to a known canonical skill name.
    Does NOT accept arbitrary English sentences or open-ended phrases.
    """
    clean_lower = re.sub(r"[•\-*]", "", raw_token).strip().lower()
    if not clean_lower or len(clean_lower) < 2 or len(clean_lower.split()) > 4:
        return None

    if clean_lower in CANONICAL_ALIASES:
        return CANONICAL_ALIASES[clean_lower]

    for _cat, skills in SKILL_TAXONOMY.items():
        for canonical_name, pattern in skills:
            if canonical_name == "Regression" and re.search(r"\bregression\s+testing\b", raw_token, re.I):
                continue
            if re.fullmatch(pattern, clean_lower, re.IGNORECASE):
                return canonical_name

    return None


def _extract_skills_from_text_block(
    lines: list[str],
) -> tuple[list[str], dict[str, str]]:
    """
    Extract canonical skills from a block of text lines with verbatim evidence.
    """
    found_skills: list[str] = []
    evidence_map: dict[str, str] = {}

    for line in lines:
        cleaned_line = re.sub(r"^[•\-\*\d\.\s]+", "", line).strip()
        if not cleaned_line:
            continue

        # 1. Delimited token scanning (for comma/slash/pipe separated skill lists)
        tokens = [t.strip() for t in re.split(r"[,|/•;]", cleaned_line) if t.strip()]
        for tok in tokens:
            canonical = resolve_known_skill(tok)
            if canonical and canonical not in found_skills:
                found_skills.append(canonical)
                evidence_map[canonical] = line

        # 2. Taxonomy pattern scanning across the line
        for _cat, skills in SKILL_TAXONOMY.items():
            for canonical_name, pattern in skills:
                # Protect QA 'regression testing' from triggering ML 'Regression'
                if canonical_name == "Regression" and re.search(r"\bregression\s+testing\b", cleaned_line, re.I):
                    continue

                if re.search(pattern, cleaned_line, re.IGNORECASE):
                    if canonical_name not in found_skills:
                        found_skills.append(canonical_name)
                        evidence_map[canonical_name] = line

    return found_skills, evidence_map


def _suppress_overlapping_skills(skills: list[str]) -> list[str]:
    """
    Eliminate duplicate substring skills (e.g. Data Structures & Algorithms subsumes DSA / Algorithms).
    """
    result: list[str] = []
    has_dsa = "Data Structures & Algorithms" in skills

    for s in skills:
        if has_dsa and s in ("DSA", "Algorithms", "Data Structures"):
            continue
        if s not in result:
            result.append(s)

    return result


# ============================================================================
# Experience & Education Extraction Helpers
# ============================================================================

def extract_experience_requirement(
    raw_text: str,
    sections: dict[str, list[str]],
    job_title: str | None = None,
) -> ExperienceRequirement:
    """Extract years of experience, seniority level, and evidence from JD."""
    # Search order covering all sections
    search_order = (
        sections.get("required", [])
        + sections.get("preferred", [])
        + sections.get("general", [])
        + sections.get("responsibilities", [])
        + sections.get("overview", [])
        + sections.get("header", [])
    )

    if not search_order:
        search_order = raw_text.splitlines()

    min_years: float | None = None
    max_years: float | None = None
    level: str | None = None
    is_required = True
    evidence: str | None = None

    # Detect Seniority Level: check title first (strongest indicator)
    if job_title:
        for pat, lvl in LEVEL_PATTERNS:
            if re.search(pat, job_title, re.IGNORECASE):
                level = lvl
                break

    # If title didn't yield a level, scan full text
    if not level:
        for pat, lvl in LEVEL_PATTERNS:
            if re.search(pat, raw_text, re.IGNORECASE):
                level = lvl
                break

    # Scan lines for experience years
    for line in search_order:
        match = EXP_RANGE_REGEX.search(line)
        if match:
            min_years = float(match.group(1))
            if match.group(2):
                max_years = float(match.group(2))
            evidence = line.strip()
            if PREFERRED_CUE_REGEX.search(line) or line in sections.get("preferred", []):
                is_required = False
            break

        plus_match = EXP_PLUS_REGEX.search(line)
        if plus_match:
            min_years = float(plus_match.group(1))
            evidence = line.strip()
            if PREFERRED_CUE_REGEX.search(line) or line in sections.get("preferred", []):
                is_required = False
            break

    return ExperienceRequirement(
        minimum_years=min_years,
        maximum_years=max_years,
        level=level,
        is_required=is_required if min_years is not None else False,
        evidence=evidence,
    )


def extract_education_requirement(
    raw_text: str,
    sections: dict[str, list[str]],
) -> EducationRequirement:
    """Extract required degree, fields of study, and evidence from JD."""
    search_order = (
        sections.get("required", [])
        + sections.get("preferred", [])
        + sections.get("general", [])
        + sections.get("overview", [])
        + sections.get("header", [])
    )

    if not search_order:
        search_order = raw_text.splitlines()

    required_degree: str | None = None
    fields_of_study: list[str] = []
    is_required = True
    evidence: str | None = None

    for line in search_order:
        # Detect Degree
        for pat, deg in DEGREE_PATTERNS:
            if re.search(pat, line, re.IGNORECASE):
                required_degree = deg
                evidence = line.strip()
                if PREFERRED_CUE_REGEX.search(line) or line in sections.get("preferred", []):
                    is_required = False
                break

        if required_degree:
            # Detect Fields of study on same line or block
            for field_pat, field_name in FIELDS_OF_STUDY_PATTERNS:
                if re.search(field_pat, line, re.IGNORECASE):
                    if field_name not in fields_of_study:
                        fields_of_study.append(field_name)
            break

    # Fallback: scan full text for disciplines if degree found but disciplines empty
    if required_degree and not fields_of_study:
        for field_pat, field_name in FIELDS_OF_STUDY_PATTERNS:
            if re.search(field_pat, raw_text, re.IGNORECASE):
                if field_name not in fields_of_study:
                    fields_of_study.append(field_name)

    return EducationRequirement(
        required_degree=required_degree,
        fields_of_study=fields_of_study,
        is_required=is_required if required_degree is not None else False,
        evidence=evidence,
    )


def extract_responsibilities(sections: dict[str, list[str]]) -> list[str]:
    """Extract bullet points or statements of responsibilities."""
    resp_lines = sections.get("responsibilities", [])
    if resp_lines:
        bullets = []
        for line in resp_lines:
            cleaned = re.sub(r"^[•\-\*\d\.\s]+", "", line).strip()
            if cleaned and len(cleaned) > 15:
                bullets.append(cleaned)
        return bullets

    # Fallback: look for action verbs in general text
    action_verb_regex = re.compile(
        r"^[•\-\*]?\s*(?:Develop|Build|Design|Implement|Architect|Collaborate|Maintain|Lead|Drive|Optimize|Write|Create|Manage)\b",
        re.IGNORECASE,
    )
    fallback: list[str] = []
    for line in sections.get("general", []):
        if action_verb_regex.match(line):
            cleaned = re.sub(r"^[•\-\*\d\.\s]+", "", line).strip()
            if cleaned and len(cleaned) > 15:
                fallback.append(cleaned)

    return fallback[:10]


def extract_keywords(raw_text: str) -> list[str]:
    """Identify high-frequency technical and architectural domain terms."""
    found: list[str] = []
    for kw in DOMAIN_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", raw_text, re.IGNORECASE):
            found.append(kw)
    return found


# ============================================================================
# Main Job Description Parser
# ============================================================================

def parse_job_description(
    text: str,
    job_title: str | None = None,
    company: str | None = None,
    location: str | None = None,
) -> ParsedJobDescription:
    """
    Parse a complete job description into structured requirements.

    Args:
        text: Raw text of the job description.
        job_title: Optional user-provided or client-provided title.
        company: Optional user-provided or client-provided company name.
        location: Optional user-provided or client-provided location / work mode.

    Returns:
        Structured ParsedJobDescription instance.

    Raises:
        ValueError: If text is empty, too short (< 50 chars / < 8 words), or excessively long (> 30000 chars).
    """
    if not text or not text.strip():
        raise ValueError("Job description cannot be empty or whitespace.")

    cleaned_text = text.strip()
    if len(cleaned_text) < 50:
        raise ValueError(
            "Job description is too short (minimum 50 characters required for meaningful analysis)."
        )

    if len(cleaned_text) > 30000:
        raise ValueError(
            "Job description exceeds maximum allowed length of 30,000 characters."
        )

    words = [w for w in cleaned_text.split() if any(c.isalnum() for c in w)]
    if len(words) < 8:
        raise ValueError(
            "Job description does not contain enough recognizable words to parse requirements."
        )

    # 1. Segment into semantic sections
    sections = segment_jd_sections(cleaned_text)

    # 2. Resolve Job Title
    final_title = job_title
    if not final_title:
        header_lines = sections["header"][:3] or sections["general"][:2]
        for line in header_lines:
            if line.lower().startswith("job title:") or line.lower().startswith("position:"):
                final_title = line.split(":", 1)[-1].strip()
                break
            m = KNOWN_TITLES_REGEX.search(line)
            if m:
                final_title = m.group(0).title()
                break

    # 3. Resolve Company Name
    final_company = company
    if not final_company:
        for line in sections["header"][:3]:
            if line.lower().startswith("company:") or line.lower().startswith("organization:"):
                final_company = line.split(":", 1)[-1].strip()
                break
            co_match = re.search(r"\b(?:at|with)\s+([A-Z][A-Za-z0-9&]+(?:\s+[A-Z][A-Za-z0-9&]+)*)\b", line)
            if co_match:
                final_company = co_match.group(1).strip()
                break

    # 4. Resolve Location
    final_location = location
    if not final_location:
        for line in sections["header"][:3]:
            if line.lower().startswith("location:"):
                final_location = line.split(":", 1)[-1].strip()
                break
            if LOCATION_TAG_REGEX.match(line):
                final_location = line
                break

    # 5. Extract Required Skills
    req_skills, req_evidence = _extract_skills_from_text_block(sections["required"])

    non_preferred_lines = (
        sections["header"]
        + sections["overview"]
        + sections["responsibilities"]
        + sections["general"]
    )

    # If no explicit required section exists, extract skills from non-preferred lines
    if not sections["required"]:
        for line in non_preferred_lines:
            if not PREFERRED_CUE_REGEX.search(line):
                s_found, s_ev = _extract_skills_from_text_block([line])
                for s in s_found:
                    if s not in req_skills:
                        req_skills.append(s)
                        req_evidence[s] = s_ev[s]
    else:
        # If required section exists, also check other lines for explicit required cues
        for line in non_preferred_lines:
            if REQUIRED_CUE_REGEX.search(line) and not PREFERRED_CUE_REGEX.search(line):
                s_found, s_ev = _extract_skills_from_text_block([line])
                for s in s_found:
                    if s not in req_skills:
                        req_skills.append(s)
                        req_evidence[s] = s_ev[s]

    # 6. Extract Preferred Skills
    pref_skills, pref_evidence = _extract_skills_from_text_block(sections["preferred"])

    # Also inspect all lines for explicit preferred cues
    all_lines = (
        sections["header"]
        + sections["overview"]
        + sections["responsibilities"]
        + sections["general"]
    )
    for line in all_lines:
        if PREFERRED_CUE_REGEX.search(line):
            p_found, p_ev = _extract_skills_from_text_block([line])
            for s in p_found:
                if s not in req_skills and s not in pref_skills:
                    pref_skills.append(s)
                    pref_evidence[s] = p_ev[s]

    # Deduplicate: Required takes strict precedence over Preferred
    pref_skills = [s for s in pref_skills if s not in req_skills]

    # Overlap suppression (Data Structures & Algorithms suppresses DSA, etc.)
    req_skills = _suppress_overlapping_skills(req_skills)
    pref_skills = _suppress_overlapping_skills(pref_skills)

    # Consolidated evidence dictionary
    consolidated_evidence = {**pref_evidence, **req_evidence}

    # 7. Extract Experience Requirements
    experience_req = extract_experience_requirement(cleaned_text, sections, job_title=final_title)

    # 8. Extract Education Requirements
    education_req = extract_education_requirement(cleaned_text, sections)

    # 9. Extract Responsibilities
    responsibilities = extract_responsibilities(sections)

    # 10. Extract High-Level Keywords
    keywords = extract_keywords(cleaned_text)

    return ParsedJobDescription(
        raw_text=cleaned_text,
        job_title=final_title,
        company=final_company,
        location=final_location,
        required_skills=req_skills,
        preferred_skills=pref_skills,
        skill_evidence=consolidated_evidence,
        experience_requirement=experience_req,
        education_requirement=education_req,
        responsibilities=responsibilities,
        keywords=keywords,
    )
