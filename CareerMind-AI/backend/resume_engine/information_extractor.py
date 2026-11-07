"""
Information extraction orchestrator for candidate resumes.

Coordinates the section segmentation and specialized parser modules:
- Contact parser (Name, email, phone, LinkedIn, GitHub, portfolio, location)
- Summary extractor (Professional summary / career objective)
- Skills parser (10 distinct technical skill categories)
- Education parser (Degrees, institutions, specializations, graduation years, CGPA/grades)
- Experience parser (Job title, company, dates, description, technologies)
- Project parser (Project name, description, technologies, project URL)
- Certifications parser (Certifications, issuing organization, dates, credential URLs)
"""

from schemas.candidate_schema import CandidateProfile
from resume_engine.section_segmenter import segment_resume_sections
from resume_engine.contact_parser import parse_contact_information
from resume_engine.skills_parser import parse_technical_skills
from resume_engine.education_parser import parse_education_entries
from resume_engine.experience_parser import parse_experience_entries
from resume_engine.project_parser import parse_project_entries
from resume_engine.certifications_parser import (
    parse_certification_entries,
    parse_achievement_entries,
)


def extract_candidate_profile(
    raw_text: str,
    links: list[str] | None = None,
) -> CandidateProfile:
    """
    Extract structured candidate information from resume text.

    Args:
        raw_text: Complete text extracted from the candidate resume.
        links: Optional hyperlink URIs discovered in document annotations.

    Returns:
        Structured and validated CandidateProfile instance.
    """
    if not raw_text or not raw_text.strip():
        return CandidateProfile()

    # 1. Segment raw text into semantic sections
    sections = segment_resume_sections(raw_text)

    # 2. Extract contact and personal information
    personal_info = parse_contact_information(
        header_lines=sections["header"],
        full_text=raw_text,
        links=links,
    )

    # 3. Extract professional summary / career objective
    professional_summary = "\n".join(sections["summary"]).strip() or None

    # 4. Extract categorized technical skills
    technical_skills = parse_technical_skills(
        skills_lines=sections["skills"],
        full_text=raw_text,
    )

    # 5. Extract educational qualifications
    education = parse_education_entries(
        education_lines=sections["education"],
    )

    # 6. Extract work experience and internships
    experience = parse_experience_entries(
        experience_lines=sections["experience"],
    )

    # 7. Extract project portfolio
    projects = parse_project_entries(
        project_lines=sections["projects"],
        links=links,
    )

    # 8. Extract professional certifications
    certifications = parse_certification_entries(
        certification_lines=sections["certifications"],
        links=links,
    )

    # 9. Extract honors, awards, and achievements
    achievements = parse_achievement_entries(
        achievement_lines=sections.get("achievements", []),
    )

    return CandidateProfile(
        personal_information=personal_info,
        professional_summary=professional_summary,
        technical_skills=technical_skills,
        education=education,
        experience=experience,
        projects=projects,
        certifications=certifications,
        achievements=achievements,
    )

