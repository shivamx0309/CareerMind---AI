"""
Section segmentation engine for resume text.

Categorizes lines of raw resume text into semantic sections:
- Header (name, contact links, address)
- Summary (professional summary, career objective)
- Skills (technical skills, competencies)
- Experience (work history, internships)
- Projects (portfolio, academic/personal projects)
- Education (degrees, colleges)
- Certifications (accredited licenses, courses, job simulations)
- Achievements (awards, coding milestones, honors, competitions)
- Other (unrecognized custom sections)
"""

import re
from typing import TypedDict


class ParsedSections(TypedDict):
    header: list[str]
    summary: list[str]
    skills: list[str]
    experience: list[str]
    projects: list[str]
    education: list[str]
    certifications: list[str]
    achievements: list[str]
    other: list[str]


# Precompiled regex patterns for standard resume section headings
SECTION_PATTERNS = [
    (
        "summary",
        re.compile(
            r"^(?:professional\s+summary|summary\s+statement|career\s+objective|executive\s+summary|profile|about\s+me|summary|objective)[\s:]*$",
            re.IGNORECASE,
        ),
    ),
    (
        "skills",
        re.compile(
            r"^(?:technical\s+skills|core\s+competencies|skills\s*(?:&|and)\s*technologies|technical\s+proficiencies|key\s+skills|skills|technologies|areas\s+of\s+expertise)[\s:]*$",
            re.IGNORECASE,
        ),
    ),
    (
        "experience",
        re.compile(
            r"^(?:work\s+experience|professional\s+experience|employment\s+history|work\s+history|career\s+history|experience|internships?|relevant\s+experience)[\s:]*$",
            re.IGNORECASE,
        ),
    ),
    (
        "projects",
        re.compile(
            r"^(?:key\s+projects|academic\s+projects|personal\s+projects|technical\s+projects|selected\s+projects|notable\s+projects|projects)[\s:]*$",
            re.IGNORECASE,
        ),
    ),
    (
        "education",
        re.compile(
            r"^(?:educational\s+background|academic\s+qualifications|academic\s+background|education|academics|qualifications)[\s:]*$",
            re.IGNORECASE,
        ),
    ),
    (
        "achievements",
        re.compile(
            r"^(?:awards?\s*(?:&|and)\s*achievements?|honors?(?:\s*(?:&|and)\s*awards?)?|achievements?|awards?|competitions?|extracurricular\s+achievements?)[\s:]*$",
            re.IGNORECASE,
        ),
    ),
    (
        "certifications",
        re.compile(
            r"^(?:licenses\s*(?:&|and)\s*certifications|certifications?\s*(?:&|and)\s*(?:job\s*simulations|courses?|licenses?)|courses?\s*(?:&|and)\s*certifications?|certifications?|certificates?|job\s*simulations?|licenses?)[\s:]*$",
            re.IGNORECASE,
        ),
    ),
]


def segment_resume_sections(text: str) -> ParsedSections:
    """
    Segment raw resume text into distinct logical sections.

    Lines before the first detected section header are assigned to 'header'.
    Subsequent lines are categorized according to the most recently detected section header.
    Unrecognized sections are collected under 'other'.
    """
    sections: ParsedSections = {
        "header": [],
        "summary": [],
        "skills": [],
        "experience": [],
        "projects": [],
        "education": [],
        "certifications": [],
        "achievements": [],
        "other": [],
    }

    if not text or not text.strip():
        return sections

    lines = [line.strip() for line in text.splitlines()]
    current_section = "header"

    for line in lines:
        if not line:
            continue

        # Check if this line is a section heading
        matched_section = None
        for sec_name, pattern in SECTION_PATTERNS:
            if pattern.match(line):
                matched_section = sec_name
                break

        if matched_section:
            current_section = matched_section
            continue

        # Check if this line is an unrecognized or other section heading
        if re.match(
            r"^(?:languages|hobbies|interests|publications|references|extracurricular(?: activities)?|volunteer(?:\s+work)?)[\s:]*$",
            line,
            re.IGNORECASE,
        ):
            current_section = "other"
            continue

        if (
            len(line.split()) <= 4
            and (line.isupper() or line.endswith(":"))
            and not line.startswith(("•", "–", "-", "*"))
            and len(line) < 35
            and current_section != "header"
        ):
            current_section = "other"
            continue

        sections[current_section].append(line)

    return sections
