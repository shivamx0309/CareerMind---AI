"""Package initialization for resume_engine."""

from resume_engine.file_validator import (
    validate_pdf_file,
    validate_file_id,
    MAX_FILE_SIZE,
)
from resume_engine.text_extractor import extract_text_from_pdf
from resume_engine.information_extractor import extract_candidate_profile
from resume_engine.contact_parser import parse_contact_information
from resume_engine.skills_parser import parse_technical_skills
from resume_engine.education_parser import parse_education_entries
from resume_engine.experience_parser import parse_experience_entries
from resume_engine.project_parser import parse_project_entries
from resume_engine.certifications_parser import (
    parse_certification_entries,
    parse_achievement_entries,
)
from resume_engine.section_segmenter import segment_resume_sections

__all__ = [
    "validate_pdf_file",
    "validate_file_id",
    "MAX_FILE_SIZE",
    "extract_text_from_pdf",
    "extract_candidate_profile",
    "parse_contact_information",
    "parse_technical_skills",
    "parse_education_entries",
    "parse_experience_entries",
    "parse_project_entries",
    "parse_certification_entries",
    "parse_achievement_entries",
    "segment_resume_sections",
]
