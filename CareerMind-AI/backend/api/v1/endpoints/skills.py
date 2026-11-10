"""
Skill Gap Analysis API Endpoints.
Provides standalone role benchmark skill gap evaluation, historical report retrieval,
and supported target role benchmark catalog querying.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.session import get_db
from schemas.skill_gap_schema import (
    SkillGapAnalysisRequest,
    SkillGapReportResponse,
    SkillGapReportSummaryResponse,
    RoleBenchmarkSummaryResponse,
)
from services import (
    career_profile_service,
    role_benchmark_service,
    skill_gap_service,
)
from services.skill_gap_service import (
    BenchmarkNotFoundError,
    ResumeNotFoundError,
    ResumeNotParsedError,
)

router = APIRouter()


@router.get(
    "/skills/roles",
    response_model=List[RoleBenchmarkSummaryResponse],
    status_code=status.HTTP_200_OK,
    summary="List available role benchmarks",
    description="Retrieve all supported standard career role benchmarks with baseline required and preferred skill expectations.",
)
async def list_role_benchmarks():
    """Return all curated role benchmarks available for skill gap analysis."""
    benchmarks = role_benchmark_service.get_role_benchmarks()
    return [
        RoleBenchmarkSummaryResponse(
            role_id=b.role_id,
            title=b.title,
            description=b.description,
            domain=b.domain,
            version=b.version,
            required_skills_count=len(b.required_skills),
            preferred_skills_count=len(b.preferred_skills),
            required_skills=[s.skill_name for s in b.required_skills],
            preferred_skills=[s.skill_name for s in b.preferred_skills],
        )
        for b in benchmarks
    ]


@router.post(
    "/skills/analyze",
    response_model=SkillGapReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Run Skill Gap Analysis against a target role",
    description="Evaluate candidate skills from an existing resume against standard role benchmarks without requiring a pasted job description.",
)
async def analyze_skill_gap_endpoint(
    request: SkillGapAnalysisRequest,
    db: Session = Depends(get_db),
):
    """Execute skill gap analysis comparing selected or default resume against benchmark."""
    profile = career_profile_service.get_or_create_local_career_profile(db)

    try:
        report = skill_gap_service.analyze_skill_gap(
            db=db,
            career_profile_id=profile.id,
            target_role=request.target_role,
            resume_id=request.resume_id,
        )
        return report

    except BenchmarkNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except ResumeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ResumeNotParsedError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.get(
    "/skills/reports",
    response_model=List[SkillGapReportSummaryResponse],
    status_code=status.HTTP_200_OK,
    summary="List historical skill gap analysis reports",
    description="Retrieve lightweight summaries of previous skill gap assessments, ordered newest first.",
)
async def list_skill_gap_reports(
    db: Session = Depends(get_db),
):
    """Retrieve all historical reports for the authenticated career profile."""
    profile = career_profile_service.get_or_create_local_career_profile(db)
    reports = skill_gap_service.get_skill_gap_reports(db, profile.id)
    return reports


@router.get(
    "/skills/reports/{report_id}",
    response_model=SkillGapReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Get full skill gap analysis report",
    description="Retrieve comprehensive details of a specific historical skill gap report by ID.",
)
async def get_skill_gap_report_endpoint(
    report_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve detailed report by ID."""
    profile = career_profile_service.get_or_create_local_career_profile(db)
    report = skill_gap_service.get_skill_gap_report(db, profile.id, report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill gap report '{report_id}' not found.",
        )
    return report


@router.delete(
    "/skills/reports/{report_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a skill gap analysis report",
    description="Permanently delete a historical skill gap report by ID.",
)
async def delete_skill_gap_report_endpoint(
    report_id: str,
    db: Session = Depends(get_db),
):
    """Delete report by ID."""
    profile = career_profile_service.get_or_create_local_career_profile(db)
    deleted = skill_gap_service.delete_skill_gap_report(db, profile.id, report_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill gap report '{report_id}' not found.",
        )
    return None

