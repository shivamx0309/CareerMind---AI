"""
Skill Gap Analysis Service.
Coordinates standalone skill gap evaluation against curated role benchmarks,
computes deterministic scores and category breakdowns, and manages persistence.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models.skill_gap_report import SkillGapReport
from database.models.resume_record import ResumeRecord
from database.models.career_profile import CareerProfile
from matching_engine.skill_matcher import (
    extract_candidate_skill_evidence,
    match_single_skill,
    SkillRequirementType,
    SkillMatchStatus,
)
from schemas.skill_gap_schema import SkillGapItem, CategoryGapBreakdown
from services.role_benchmark_service import get_role_benchmark, RoleBenchmark
from services.resume_library_service import (
    reconstitute_candidate_profile,
    get_default_resume_record,
)


class SkillGapServiceError(Exception):
    """Base exception for skill gap service errors."""
    pass


class BenchmarkNotFoundError(SkillGapServiceError):
    """Raised when the requested role benchmark is not supported."""
    pass


class ResumeNotFoundError(SkillGapServiceError):
    """Raised when the specified resume record cannot be found."""
    pass


class ResumeNotParsedError(SkillGapServiceError):
    """Raised when the resume record has not been successfully parsed."""
    pass


def analyze_skill_gap(
    db: Session,
    career_profile_id: str,
    target_role: str,
    resume_id: Optional[str] = None,
) -> SkillGapReport:
    """
    Perform standalone skill gap analysis comparing a candidate's resume
    against a target role benchmark.

    Parameters:
        db: Active SQLAlchemy database session.
        career_profile_id: ID of the authenticated user's career profile.
        target_role: Benchmark identifier (e.g., 'sde', 'backend_developer').
        resume_id: Optional specific ResumeRecord ID or file_id. If omitted,
                   the user's default resume is selected.

    Returns:
        Persisted SkillGapReport model instance.
    """
    # 1. Validate Benchmark
    benchmark: Optional[RoleBenchmark] = get_role_benchmark(target_role)
    if not benchmark:
        raise BenchmarkNotFoundError(
            f"Target role '{target_role}' is not supported. Please select a valid role from the catalog."
        )

    # 2. Resolve Resume Record
    record: Optional[ResumeRecord] = None
    if resume_id and resume_id.strip():
        search_id = resume_id.strip()
        stmt = select(ResumeRecord).where(
            (ResumeRecord.career_profile_id == career_profile_id)
            & ((ResumeRecord.id == search_id) | (ResumeRecord.file_id == search_id))
        )
        record = db.execute(stmt).scalar_one_or_none()
        if not record:
            raise ResumeNotFoundError(
                f"Resume with ID '{search_id}' was not found in your resume library."
            )
    else:
        record = get_default_resume_record(db, career_profile_id)
        if not record:
            # Fallback to the latest resume record for the career profile
            stmt = (
                select(ResumeRecord)
                .where(ResumeRecord.career_profile_id == career_profile_id)
                .order_by(ResumeRecord.created_at.desc())
            )
            record = db.execute(stmt).scalars().first()
            if not record:
                raise ResumeNotFoundError(
                    "No resume found in your resume library. Please upload a resume first."
                )

    # 3. Verify Parsing Status
    if record.parsing_status != "completed":
        raise ResumeNotParsedError(
            f"Resume '{record.display_name or record.original_filename}' has not been parsed "
            f"(current status: '{record.parsing_status}'). Please parse the resume before running analysis."
        )

    # 4. Reconstitute Candidate Profile
    candidate_profile = reconstitute_candidate_profile(db, record.id)
    if not candidate_profile:
        raise ResumeNotParsedError(
            f"Parsed profile data could not be reconstituted for resume '{record.display_name or record.original_filename}'."
        )

    # 5. Extract Evidence Index
    evidence_index = extract_candidate_skill_evidence(candidate_profile)
    has_candidate_evidence = any(len(records) > 0 for records in evidence_index.values())

    # 6. Evaluate Benchmark Skills
    matched_skills: List[Dict[str, Any]] = []
    related_skills: List[Dict[str, Any]] = []
    missing_required_skills: List[str] = []
    missing_preferred_skills: List[str] = []

    matched_required_count = 0
    related_required_count = 0
    missing_required_count = 0

    matched_preferred_count = 0
    related_preferred_count = 0
    missing_preferred_count = 0

    total_weighted_score = 0.0
    total_weights = 0.0

    # Group skills for category breakdown
    category_map: Dict[str, Dict[str, Any]] = {}

    def ensure_category_entry(cat: str):
        if cat not in category_map:
            category_map[cat] = {
                "category": cat,
                "total_skills": 0,
                "matched_count": 0,
                "related_count": 0,
                "missing_count": 0,
            }

    # Evaluate Required Skills
    for b_skill in benchmark.required_skills:
        cat = b_skill.category
        ensure_category_entry(cat)
        category_map[cat]["total_skills"] += 1

        match_res = match_single_skill(
            skill_name=b_skill.skill_name,
            requirement_type=SkillRequirementType.REQUIRED,
            evidence_index=evidence_index,
        )

        weight = b_skill.weight  # typically 1.0
        total_weights += weight

        if match_res.status in (SkillMatchStatus.EXACT_MATCH, SkillMatchStatus.ALIAS_MATCH):
            matched_required_count += 1
            total_weighted_score += 1.0 * weight
            category_map[cat]["matched_count"] += 1
            matched_skills.append({
                "skill_name": b_skill.skill_name,
                "category": cat,
                "importance": "required",
                "status": match_res.status.value,
                "match_confidence": 1.0,
                "weight": weight,
                "matched_skill": match_res.candidate_evidence or b_skill.skill_name,
                "evidence_source": match_res.evidence_source,
                "evidence_context": match_res.candidate_evidence,
            })
        elif match_res.status == SkillMatchStatus.SEMANTICALLY_RELATED:
            related_required_count += 1
            total_weighted_score += 0.6 * weight
            category_map[cat]["related_count"] += 1
            related_skills.append({
                "skill_name": b_skill.skill_name,
                "category": cat,
                "importance": "required",
                "status": match_res.status.value,
                "match_confidence": 0.6,
                "weight": weight,
                "matched_skill": match_res.candidate_evidence or b_skill.skill_name,
                "evidence_source": match_res.evidence_source,
                "evidence_context": match_res.candidate_evidence,
            })
        else:  # MISSING
            missing_required_count += 1
            total_weighted_score += 0.0
            category_map[cat]["missing_count"] += 1
            missing_required_skills.append(b_skill.skill_name)

    # Evaluate Preferred Skills
    for b_skill in benchmark.preferred_skills:
        cat = b_skill.category
        ensure_category_entry(cat)
        category_map[cat]["total_skills"] += 1

        match_res = match_single_skill(
            skill_name=b_skill.skill_name,
            requirement_type=SkillRequirementType.PREFERRED,
            evidence_index=evidence_index,
        )

        weight = b_skill.weight  # typically 0.5
        total_weights += weight

        if match_res.status in (SkillMatchStatus.EXACT_MATCH, SkillMatchStatus.ALIAS_MATCH):
            matched_preferred_count += 1
            total_weighted_score += 1.0 * weight
            category_map[cat]["matched_count"] += 1
            matched_skills.append({
                "skill_name": b_skill.skill_name,
                "category": cat,
                "importance": "preferred",
                "status": match_res.status.value,
                "match_confidence": 1.0,
                "weight": weight,
                "matched_skill": match_res.candidate_evidence or b_skill.skill_name,
                "evidence_source": match_res.evidence_source,
                "evidence_context": match_res.candidate_evidence,
            })
        elif match_res.status == SkillMatchStatus.SEMANTICALLY_RELATED:
            related_preferred_count += 1
            total_weighted_score += 0.6 * weight
            category_map[cat]["related_count"] += 1
            related_skills.append({
                "skill_name": b_skill.skill_name,
                "category": cat,
                "importance": "preferred",
                "status": match_res.status.value,
                "match_confidence": 0.6,
                "weight": weight,
                "matched_skill": match_res.candidate_evidence or b_skill.skill_name,
                "evidence_source": match_res.evidence_source,
                "evidence_context": match_res.candidate_evidence,
            })
        else:  # MISSING
            missing_preferred_count += 1
            total_weighted_score += 0.0
            category_map[cat]["missing_count"] += 1
            missing_preferred_skills.append(b_skill.skill_name)

    # 7. Compute Scores & Coverages
    total_required = benchmark.total_required
    total_preferred = benchmark.total_preferred

    if not has_candidate_evidence:
        analysis_status = "no_candidate_skills"
        overall_score = 0.0
        required_coverage_percentage = 0.0
        preferred_coverage_percentage = 0.0 if total_preferred > 0 else 100.0
    elif total_required == 0:
        analysis_status = "insufficient_benchmark"
        overall_score = None
        required_coverage_percentage = None
        preferred_coverage_percentage = (
            round((matched_preferred_count / total_preferred) * 100, 1)
            if total_preferred > 0
            else 100.0
        )
    else:
        analysis_status = "completed"
        if total_weights > 0:
            overall_score = round((total_weighted_score / total_weights) * 100, 1)
        else:
            overall_score = 0.0
        required_coverage_percentage = round((matched_required_count / total_required) * 100, 1)
        preferred_coverage_percentage = (
            round((matched_preferred_count / total_preferred) * 100, 1)
            if total_preferred > 0
            else 100.0
        )

    # 8. Compute Category Breakdown
    category_breakdown: List[Dict[str, Any]] = []
    for cat, data in sorted(category_map.items()):
        tot = data["total_skills"]
        m_cnt = data["matched_count"]
        r_cnt = data["related_count"]
        cov = round(((m_cnt * 1.0 + r_cnt * 0.6) / tot) * 100, 1) if tot > 0 else 0.0
        category_breakdown.append({
            "category": cat,
            "total_skills": tot,
            "matched_count": m_cnt,
            "related_count": r_cnt,
            "missing_count": data["missing_count"],
            "coverage_percentage": cov,
        })

    # 9. Persist Report Entity
    report = SkillGapReport(
        id=str(uuid.uuid4()),
        career_profile_id=career_profile_id,
        resume_record_id=record.id,
        target_role=benchmark.role_id,
        role_title=benchmark.title,
        benchmark_version=benchmark.version,
        overall_score=overall_score,
        required_coverage_percentage=required_coverage_percentage,
        preferred_coverage_percentage=preferred_coverage_percentage,
        total_required_skills=total_required,
        matched_required_skills_count=matched_required_count,
        related_required_skills_count=related_required_count,
        missing_required_skills_count=missing_required_count,
        total_preferred_skills=total_preferred,
        matched_preferred_skills_count=matched_preferred_count,
        related_preferred_skills_count=related_preferred_count,
        missing_preferred_skills_count=missing_preferred_count,
        matched_skills=matched_skills,
        related_skills=related_skills,
        missing_required_skills=missing_required_skills,
        missing_preferred_skills=missing_preferred_skills,
        category_breakdown=category_breakdown,
        analysis_status=analysis_status,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return report


def get_skill_gap_reports(
    db: Session,
    career_profile_id: str,
) -> List[SkillGapReport]:
    """Retrieve all historical skill gap reports for a career profile, ordered by newest first."""
    stmt = (
        select(SkillGapReport)
        .where(SkillGapReport.career_profile_id == career_profile_id)
        .order_by(SkillGapReport.created_at.desc())
    )
    return list(db.execute(stmt).scalars().all())


def get_skill_gap_report(
    db: Session,
    career_profile_id: str,
    report_id: str,
) -> Optional[SkillGapReport]:
    """Retrieve a specific skill gap report by ID for a career profile."""
    stmt = select(SkillGapReport).where(
        (SkillGapReport.id == report_id)
        & (SkillGapReport.career_profile_id == career_profile_id)
    )
    return db.execute(stmt).scalar_one_or_none()


def delete_skill_gap_report(
    db: Session,
    career_profile_id: str,
    report_id: str,
) -> bool:
    """Delete a specific skill gap report. Returns True if deleted, False if not found."""
    report = get_skill_gap_report(db, career_profile_id, report_id)
    if not report:
        return False

    db.delete(report)
    db.commit()
    return True
