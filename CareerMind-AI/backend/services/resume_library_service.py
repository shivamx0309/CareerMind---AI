"""
Resume library service managing resume records, default selection, and two-way CandidateProfile mapping.
"""

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import select, update

from database.models.resume_record import ResumeRecord
from database.models.resume_profile import ResumeProfile
from database.models.resume_skill import ResumeSkill
from database.models.resume_education import ResumeEducation
from database.models.resume_experience import ResumeExperience
from database.models.resume_project import ResumeProject
from database.models.resume_certification import ResumeCertification
from schemas.candidate_schema import (
    CandidateProfile,
    PersonalInformation,
    TechnicalSkills,
    EducationEntry,
    ExperienceEntry,
    ProjectEntry,
    CertificationEntry,
    AchievementEntry,
)

HEX_32_REGEX = re.compile(r"^[0-9a-f]{32}$", re.IGNORECASE)

# Backend and project roots
BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"


def validate_file_id_format(file_id: str) -> str:
    """Validate that file_id is strictly a 32-character hexadecimal string."""
    if not file_id or not isinstance(file_id, str):
        raise ValueError("Invalid file ID: must be a non-empty string.")
    cleaned = file_id.strip().lower()
    if not HEX_32_REGEX.match(cleaned):
        raise ValueError(f"Invalid file ID format: '{file_id}'. Must be a 32-char hex string.")
    return cleaned


def derive_server_file_path(file_id: str) -> Path:
    """
    Derive the secure physical PDF path server-side from the validated file_id.
    Never trusts client-supplied file paths.
    """
    validated_id = validate_file_id_format(file_id)
    upload_dir_resolved = UPLOAD_DIR.resolve()
    target_path = (UPLOAD_DIR / f"{validated_id}.pdf").resolve()

    # Prevent path traversal outside uploads directory
    try:
        target_path.relative_to(upload_dir_resolved)
    except ValueError as exc:
        raise ValueError("Invalid file path: path traversal detected.") from exc

    return target_path


def register_uploaded_resume(
    db: Session,
    career_profile_id: str,
    file_id: str,
    original_filename: str,
    file_size: int,
    display_name: Optional[str] = None,
) -> ResumeRecord:
    """
    Register an uploaded resume file record under a career profile.
    Derives the server file path automatically and manages default status.
    """
    validated_id = validate_file_id_format(file_id)
    resolved_path = derive_server_file_path(validated_id)

    # Check for existing record with this file_id
    stmt = select(ResumeRecord).where(ResumeRecord.file_id == validated_id)
    existing = db.execute(stmt).scalar_one_or_none()
    if existing:
        raise ValueError(f"Resume with file_id '{validated_id}' is already registered.")

    # Determine if this should be the default resume
    count_stmt = select(ResumeRecord).where(ResumeRecord.career_profile_id == career_profile_id)
    existing_count = len(db.execute(count_stmt).scalars().all())
    is_default = (existing_count == 0)

    clean_display_name = display_name.strip() if display_name else original_filename

    new_record = ResumeRecord(
        career_profile_id=career_profile_id,
        file_id=validated_id,
        display_name=clean_display_name,
        original_filename=original_filename,
        file_path=str(resolved_path),
        file_size=file_size,
        is_default=is_default,
        upload_status="completed",
        extraction_status="pending",
        parsing_status="pending",
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record


def set_default_resume(
    db: Session,
    career_profile_id: str,
    resume_record_id: str,
) -> ResumeRecord:
    """
    Atomically designate a target resume as the default for the career profile.
    Clears the previous default inside the same transaction to satisfy the partial unique index.
    """
    target = db.get(ResumeRecord, resume_record_id)
    if not target or target.career_profile_id != career_profile_id:
        raise ValueError(f"ResumeRecord '{resume_record_id}' not found for profile '{career_profile_id}'.")

    if target.is_default:
        return target

    # Atomic switch
    with db.begin_nested():
        # Clear existing default
        db.execute(
            update(ResumeRecord)
            .where(
                ResumeRecord.career_profile_id == career_profile_id,
                ResumeRecord.is_default == True,
            )
            .values(is_default=False)
        )
        # Set target default
        target.is_default = True

    db.commit()
    db.refresh(target)
    return target


def delete_resume_record(
    db: Session,
    career_profile_id: str,
    resume_record_id: str,
) -> bool:
    """
    Delete a resume record and its parsed profile children.
    If the deleted resume was default, promotes the most recently updated remaining resume.
    """
    target = db.get(ResumeRecord, resume_record_id)
    if not target or target.career_profile_id != career_profile_id:
        return False

    was_default = target.is_default
    db.delete(target)
    db.flush()

    if was_default:
        # Promote the most recently updated remaining resume
        stmt = (
            select(ResumeRecord)
            .where(ResumeRecord.career_profile_id == career_profile_id)
            .order_by(ResumeRecord.updated_at.desc())
            .limit(1)
        )
        remaining = db.execute(stmt).scalar_one_or_none()
        if remaining:
            remaining.is_default = True

    db.commit()
    return True


def rename_resume_record(
    db: Session,
    resume_record_id: str,
    new_display_name: str,
) -> Optional[ResumeRecord]:
    """Update the user-facing display name of a resume record."""
    target = db.get(ResumeRecord, resume_record_id)
    if not target:
        return None

    target.display_name = new_display_name.strip()
    db.commit()
    db.refresh(target)
    return target


def get_resume_records(
    db: Session,
    career_profile_id: str,
) -> List[ResumeRecord]:
    """Retrieve all resume records for a career profile ordered by default then creation date."""
    stmt = (
        select(ResumeRecord)
        .where(ResumeRecord.career_profile_id == career_profile_id)
        .order_by(ResumeRecord.is_default.desc(), ResumeRecord.created_at.desc())
    )
    return list(db.execute(stmt).scalars().all())


# =============================================================================
# Two-Way CandidateProfile Persistence & Reconstitution
# =============================================================================

TECHNICAL_SKILL_CATEGORIES = [
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
]


def persist_parsed_candidate_profile(
    db: Session,
    resume_record_id: str,
    candidate: CandidateProfile,
) -> ResumeProfile:
    """
    Persist a parsed CandidateProfile into independent relational resume entities.
    Replaces any prior parsed profile for this specific resume record.
    """
    record = db.get(ResumeRecord, resume_record_id)
    if not record:
        raise ValueError(f"ResumeRecord '{resume_record_id}' does not exist.")

    # Remove prior parsed profile if present
    stmt = select(ResumeProfile).where(ResumeProfile.resume_record_id == resume_record_id)
    existing_profile = db.execute(stmt).scalar_one_or_none()
    if existing_profile:
        db.delete(existing_profile)
        db.flush()

    p_info = candidate.personal_information or PersonalInformation()

    # Create root ResumeProfile
    achievements_data = [
        a.model_dump() if hasattr(a, "model_dump") else a
        for a in (candidate.achievements or [])
    ]

    rp = ResumeProfile(
        resume_record_id=resume_record_id,
        full_name=p_info.full_name,
        email=p_info.email,
        phone=p_info.phone,
        linkedin=p_info.linkedin,
        github=p_info.github,
        portfolio=p_info.portfolio,
        location=p_info.location,
        professional_summary=candidate.professional_summary,
        achievements=achievements_data,
    )
    db.add(rp)
    db.flush()  # Generates rp.id

    # Persist all 10 TechnicalSkills categories
    ts = candidate.technical_skills or TechnicalSkills()
    for cat in TECHNICAL_SKILL_CATEGORIES:
        skill_list = getattr(ts, cat, []) or []
        for sk in skill_list:
            db.add(
                ResumeSkill(
                    resume_profile_id=rp.id,
                    skill_name=sk,
                    category=cat,
                    confidence=1.0,
                )
            )

    # Persist Education entries
    for edu in candidate.education or []:
        db.add(
            ResumeEducation(
                resume_profile_id=rp.id,
                degree=edu.degree,
                institution=edu.institution,
                specialization=edu.specialization,
                start_year=edu.start_year,
                end_year=edu.end_year,
                grade_or_cgpa=edu.grade_or_cgpa,
            )
        )

    # Persist Experience entries
    for exp in candidate.experience or []:
        db.add(
            ResumeExperience(
                resume_profile_id=rp.id,
                job_title=exp.job_title,
                company=exp.company,
                employment_type=exp.employment_type,
                location=exp.location,
                start_date=exp.start_date,
                end_date=exp.end_date,
                description=exp.description,
                technologies=exp.technologies or [],
            )
        )

    # Persist Project entries
    for proj in candidate.projects or []:
        db.add(
            ResumeProject(
                resume_profile_id=rp.id,
                project_name=proj.project_name,
                description=proj.description,
                technologies=proj.technologies or [],
                project_url=proj.project_url,
            )
        )

    # Persist Certification entries
    for cert in candidate.certifications or []:
        db.add(
            ResumeCertification(
                resume_profile_id=rp.id,
                certification_name=cert.certification_name,
                issuing_organization=cert.issuing_organization,
                issue_date=cert.issue_date,
                credential_url=cert.credential_url,
            )
        )

    # Update resume record status
    record.parsing_status = "completed"
    record.last_parsed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(rp)
    return rp


def reconstitute_candidate_profile(
    db: Session,
    resume_record_id: str,
) -> Optional[CandidateProfile]:
    """
    Reconstitute the exact Pydantic CandidateProfile from the database
    with 100% data fidelity, preserving field types and response contracts.
    """
    stmt = select(ResumeProfile).where(ResumeProfile.resume_record_id == resume_record_id)
    rp = db.execute(stmt).scalar_one_or_none()
    if not rp:
        return None

    # Reconstruct PersonalInformation
    personal_info = PersonalInformation(
        full_name=rp.full_name,
        email=rp.email,
        phone=rp.phone,
        linkedin=rp.linkedin,
        github=rp.github,
        portfolio=rp.portfolio,
        location=rp.location,
    )

    # Reconstruct TechnicalSkills across all 10 categories
    skills_stmt = select(ResumeSkill).where(ResumeSkill.resume_profile_id == rp.id)
    skills = db.execute(skills_stmt).scalars().all()

    skills_dict = {cat: [] for cat in TECHNICAL_SKILL_CATEGORIES}
    for sk in skills:
        if sk.category in skills_dict:
            skills_dict[sk.category].append(sk.skill_name)

    tech_skills = TechnicalSkills(**skills_dict)

    # Reconstruct Education entries
    edu_stmt = select(ResumeEducation).where(ResumeEducation.resume_profile_id == rp.id)
    educations = [
        EducationEntry(
            degree=e.degree,
            institution=e.institution,
            specialization=e.specialization,
            start_year=e.start_year,
            end_year=e.end_year,
            grade_or_cgpa=e.grade_or_cgpa,
        )
        for e in db.execute(edu_stmt).scalars().all()
    ]

    # Reconstruct Experience entries
    exp_stmt = select(ResumeExperience).where(ResumeExperience.resume_profile_id == rp.id)
    experiences = [
        ExperienceEntry(
            job_title=x.job_title,
            company=x.company,
            employment_type=x.employment_type,
            location=x.location,
            start_date=x.start_date,
            end_date=x.end_date,
            description=x.description,
            technologies=x.technologies or [],
        )
        for x in db.execute(exp_stmt).scalars().all()
    ]

    # Reconstruct Project entries
    proj_stmt = select(ResumeProject).where(ResumeProject.resume_profile_id == rp.id)
    projects = [
        ProjectEntry(
            project_name=p.project_name,
            description=p.description,
            technologies=p.technologies or [],
            project_url=p.project_url,
        )
        for p in db.execute(proj_stmt).scalars().all()
    ]

    # Reconstruct Certification entries
    cert_stmt = select(ResumeCertification).where(ResumeCertification.resume_profile_id == rp.id)
    certifications = [
        CertificationEntry(
            certification_name=c.certification_name,
            issuing_organization=c.issuing_organization,
            issue_date=c.issue_date,
            credential_url=c.credential_url,
        )
        for c in db.execute(cert_stmt).scalars().all()
    ]

    # Reconstruct Achievement entries
    achievements = [
        AchievementEntry(**a)
        for a in (rp.achievements or [])
    ]

    return CandidateProfile(
        personal_information=personal_info,
        professional_summary=rp.professional_summary,
        technical_skills=tech_skills,
        education=educations,
        experience=experiences,
        projects=projects,
        certifications=certifications,
        achievements=achievements,
    )

