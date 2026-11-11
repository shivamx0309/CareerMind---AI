"""
Job Matching Service Orchestrator (Phase 5.6).

Coordinates all Phase 5 intelligent matching modules into a cohesive,
evidence-based assessment pipeline:
1. Validates file ID and checks for directory traversal
2. Retrieves and extracts candidate profile text and structured entities
3. Parses target job description into structured requirements
4. Evaluates technical skills, experience tenure, and education credentials
5. Calculates deterministic lexical similarity and explainable component match scores
6. Generates prioritized, actionable recommendations
7. Assembles a safe, comprehensive JobMatchResponse without leaking private PII
"""

import logging
from datetime import datetime, timezone
from pathlib import Path

from resume_engine.file_validator import validate_file_id
from resume_engine.text_extractor import extract_text_from_pdf
from resume_engine.information_extractor import extract_candidate_profile
from schemas.candidate_schema import CandidateProfile
from schemas.matching_schema import (
    ParsedJobDescription,
    SkillMatchItem,
    SkillMatchStatus,
    SkillRequirementType,
    ExperienceMatchResult,
    EducationMatchResult,
    MatchScoreBreakdown,
    CandidateMatchSummary,
    MatchAnalysisMetadata,
    JobMatchResponse,
)
from matching_engine.jd_parser import parse_job_description
from matching_engine.skill_matcher import match_candidate_skills
from matching_engine.experience_matcher import match_candidate_experience
from matching_engine.education_matcher import match_candidate_education
from matching_engine.score_calculator import calculate_match_score, DEFAULT_WEIGHTS
from matching_engine.recommendation_engine import generate_recommendations
from services.storage_service import UPLOAD_DIR as DEFAULT_UPLOAD_DIR

logger = logging.getLogger(__name__)


def count_unique_candidate_skills(profile: CandidateProfile) -> int:
    """Calculate the total unique technical skills present on a candidate profile."""
    if not profile or not profile.technical_skills:
        return 0

    skills_set = set()
    ts = profile.technical_skills
    for category in [
        ts.programming_languages,
        ts.frontend,
        ts.backend,
        ts.databases,
        ts.data_analytics,
        ts.machine_learning,
        ts.deep_learning,
        ts.cloud_devops,
        ts.tools,
        ts.other,
    ]:
        for s in category:
            if s and s.strip():
                skills_set.add(s.strip().lower())
    return len(skills_set)


def execute_job_matching(
    file_id: str,
    job_description: str,
    job_title: str | None = None,
    company: str | None = None,
    location: str | None = None,
    upload_dir: Path | None = None,
    custom_weights: dict[str, float] | None = None,
) -> JobMatchResponse:
    """
    Execute end-to-end evidence-based matching of a candidate resume against a job description.

    Args:
        file_id: 32-character hexadecimal UUID of the uploaded resume PDF.
        job_description: Target job posting text.
        job_title: Optional explicit job title.
        company: Optional hiring company name.
        location: Optional job location.
        upload_dir: Optional custom upload directory (for tests/environments).
        custom_weights: Optional custom weight dictionary summing to 1.0.

    Returns:
        Structured JobMatchResponse containing explainable scores, breakdown,
        skill evaluations, experience/education assessments, and actionable recommendations.

    Raises:
        ValueError: If file_id is invalid or PDF text is empty/corrupt.
        FileNotFoundError: If PDF resume does not exist.
        PermissionError: If path traversal is attempted.
    """
    # 1. Validate File ID
    validated_file_id = validate_file_id(file_id)

    # 2. Resolve PDF Path and Guard Against Traversal
    effective_upload_dir = (upload_dir or DEFAULT_UPLOAD_DIR).resolve()
    stored_path = (effective_upload_dir / f"{validated_file_id}.pdf").resolve()

    try:
        stored_path.relative_to(effective_upload_dir)
    except ValueError as exc:
        logger.warning("Path traversal attempt blocked for file_id %s", validated_file_id)
        raise PermissionError("Invalid file path.") from exc

    if not stored_path.exists() or not stored_path.is_file():
        logger.info("Resume file not found for file_id %s", validated_file_id)
        raise FileNotFoundError(f"Resume file '{validated_file_id}' not found.")

    # 3. Extract Text & Parse Candidate Profile
    try:
        extraction_data = extract_text_from_pdf(str(stored_path))
    except Exception as exc:
        logger.error("Text extraction failed for file_id %s: %s", validated_file_id, exc)
        raise ValueError("Unable to extract text from the PDF document.") from exc

    raw_text = extraction_data.get("full_text", "")
    if extraction_data.get("extraction_status") == "no_text_found" or not raw_text.strip():
        logger.info("No readable text found for file_id %s", validated_file_id)
        raise ValueError("No readable text found in the resume PDF.")

    candidate_profile = extract_candidate_profile(
        raw_text=raw_text,
        links=extraction_data.get("links"),
    )
    if candidate_profile is None:
        logger.error("Candidate profile extraction returned None for file_id %s", validated_file_id)
        raise ValueError("Unable to parse candidate profile from resume.")

    # 4. Parse Job Description
    parsed_jd = parse_job_description(
        text=job_description,
        job_title=job_title,
        company=company,
        location=location,
    )

    # 5. Evaluate Technical Skills
    matched_skills, missing_required_skills, missing_preferred_skills = match_candidate_skills(
        candidate_profile, parsed_jd
    )

    related_skills = [
        m for m in matched_skills if m.status == SkillMatchStatus.SEMANTICALLY_RELATED
    ]

    # 6. Evaluate Experience & Education
    experience_match = match_candidate_experience(candidate_profile, parsed_jd)
    education_match = match_candidate_education(candidate_profile, parsed_jd)

    # 7. Calculate Explainable Match Score
    match_score = calculate_match_score(
        parsed_jd=parsed_jd,
        skill_matches=matched_skills,
        experience_match=experience_match,
        education_match=education_match,
        candidate=candidate_profile,
        candidate_text=raw_text,
        weights=custom_weights,
    )

    # 8. Generate Actionable Recommendations
    recommendations = generate_recommendations(
        parsed_jd=parsed_jd,
        matched_skills=matched_skills,
        experience_match=experience_match,
        education_match=education_match,
        score_breakdown=match_score,
    )

    # 9. Build Safe Candidate Summary (without leaking full contact details or PII)
    candidate_summary = CandidateMatchSummary(
        total_skills_count=count_unique_candidate_skills(candidate_profile),
        professional_experience_years=experience_match.professional_years,
        highest_degree=(
            candidate_profile.education[0].degree
            if candidate_profile.education and candidate_profile.education[0].degree
            else None
        ),
        projects_count=len(candidate_profile.projects),
    )

    # 10. Construct Metadata
    metadata = MatchAnalysisMetadata(
        timestamp=datetime.now(timezone.utc).isoformat(),
        engine_version="5.6.0",
        scoring_weights=dict(custom_weights or DEFAULT_WEIGHTS),
        components_assessed=list(match_score.components.keys()),
    )

    # 11. Assemble Consolidated Response
    return JobMatchResponse(
        success=True,
        file_id=validated_file_id,
        parsed_job=parsed_jd,
        candidate_summary=candidate_summary,
        match_score=match_score,
        overall_score=match_score.overall_score,
        match_classification=match_score.match_classification,
        matched_skills=matched_skills,
        related_skills=related_skills,
        missing_required_skills=missing_required_skills,
        missing_preferred_skills=missing_preferred_skills,
        experience_match=experience_match,
        education_match=education_match,
        recommendations=recommendations,
        metadata=metadata,
    )
