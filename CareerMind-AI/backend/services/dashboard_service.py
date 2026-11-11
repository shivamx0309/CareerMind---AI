"""
Service layer for CareerMind AI Centralized Dashboard Career Insights (Phase 6).

Aggregates authoritative saved candidate telemetry across:
1. Career Profile
2. Resume Intelligence & Extracted Competencies
3. Job Matching Persistence
4. Skill Gap Benchmark Analyses
5. Personalized Learning Roadmap & Progress Telemetry
6. AI Mock Interview History & Reports
"""

import json
import logging
from typing import List, Optional
from sqlalchemy.orm import Session

from database.models import (
    CareerProfile,
    ResumeRecord,
    ResumeProfile,
    SkillGapReport,
    LearningRoadmap,
    InterviewSession,
)
from schemas.dashboard_schema import (
    CareerProfileSummary,
    ResumeInsights,
    JobMatchInsights,
    SkillGapInsights,
    LearningRoadmapInsights,
    MockInterviewInsights,
    DashboardInsightsResponse,
)
from services import career_profile_service, roadmap_service

logger = logging.getLogger(__name__)


def get_dashboard_insights(
    db: Session,
    user_id: str = "local_user",
) -> DashboardInsightsResponse:
    """
    Generate complete, explainable career insights for the dashboard.
    Reuses existing database models and services without inventing or fabricating data.
    """
    # 1. Resolve Career Profile
    profile = career_profile_service.get_or_create_local_career_profile(db)

    # Decode preferred locations safely
    pref_locations: List[str] = []
    if profile.preferred_locations:
        if isinstance(profile.preferred_locations, list):
            pref_locations = profile.preferred_locations
        elif isinstance(profile.preferred_locations, str):
            try:
                parsed_locs = json.loads(profile.preferred_locations)
                if isinstance(parsed_locs, list):
                    pref_locations = parsed_locs
                else:
                    pref_locations = [str(parsed_locs)]
            except Exception:
                pref_locations = [profile.preferred_locations]

    # 2. Resolve Active/Default Resume
    # Priority: 1. is_default and parsed -> 2. any parsed resume (newest first) -> 3. default (even if pending) -> 4. newest record
    all_resumes = (
        db.query(ResumeRecord)
        .filter(ResumeRecord.career_profile_id == profile.id)
        .order_by(ResumeRecord.is_default.desc(), ResumeRecord.created_at.desc())
        .all()
    )

    active_resume: Optional[ResumeRecord] = None
    # Check default parsed
    for r in all_resumes:
        if r.is_default and r.parsing_status == "completed":
            active_resume = r
            break

    # If no default is parsed, find newest parsed
    if not active_resume:
        for r in all_resumes:
            if r.parsing_status == "completed":
                active_resume = r
                break

    # If no parsed resume exists, take default or newest
    if not active_resume and all_resumes:
        active_resume = all_resumes[0]

    # Build Resume Insights
    if not active_resume:
        resume_insights = ResumeInsights(
            has_resume=False,
            status="Not Uploaded",
            resume_name=None,
            is_default=False,
            total_skills=0,
            education_count=0,
            experience_count=0,
            project_count=0,
            certification_count=0,
            top_skills=[],
        )
        tech_skills_count = 0
        projects_count = 0
        certifications_count = 0
    else:
        # Determine status string
        if active_resume.parsing_status == "completed":
            status_label = "Parsed"
        elif active_resume.parsing_status == "failed":
            status_label = "Parsing Failed"
        elif active_resume.upload_status == "completed":
            status_label = "Uploaded"
        else:
            status_label = active_resume.upload_status.capitalize()

        rp: Optional[ResumeProfile] = active_resume.resume_profile
        skills_list = [s.skill_name for s in rp.skills] if (rp and rp.skills) else []
        edu_count = len(rp.educations) if (rp and rp.educations) else 0
        exp_count = len(rp.experiences) if (rp and rp.experiences) else 0
        proj_count = len(rp.projects) if (rp and rp.projects) else 0
        cert_count = len(rp.certifications) if (rp and rp.certifications) else 0

        tech_skills_count = len(skills_list)
        projects_count = proj_count
        certifications_count = cert_count

        resume_insights = ResumeInsights(
            has_resume=True,
            status=status_label,
            resume_id=active_resume.id,
            file_id=active_resume.file_id,
            display_name=active_resume.display_name or active_resume.original_filename,
            is_default=bool(active_resume.is_default),
            total_skills=tech_skills_count,
            education_count=edu_count,
            experience_count=exp_count,
            project_count=proj_count,
            certification_count=cert_count,
            uploaded_at=active_resume.created_at,
            last_parsed_at=active_resume.last_parsed_at,
            top_skills=skills_list[:8],
        )

    # 3. Build Career Profile Summary
    # Derive reliable experience summary
    if profile.career_status and profile.career_status.lower() == "fresher":
        exp_summary = "Fresher"
    elif active_resume and active_resume.resume_profile and active_resume.resume_profile.experiences:
        num_exp = len(active_resume.resume_profile.experiences)
        exp_summary = f"{num_exp} Position(s) recorded"
    else:
        exp_summary = profile.career_status or "Not provided"

    profile_summary = CareerProfileSummary(
        profile_id=profile.id,
        user_id=profile.user_id,
        full_name=profile.full_name or "Candidate",
        career_status=profile.career_status or "Fresher",
        primary_target_role=profile.primary_target_role or "Target Role",
        highest_education=profile.highest_education,
        degree=profile.degree,
        institution=profile.institution,
        graduation_year=profile.graduation_year,
        preferred_job_type=profile.preferred_job_type,
        preferred_work_mode=profile.preferred_work_mode,
        preferred_locations=pref_locations,
        total_experience_summary=exp_summary,
        technical_skills_count=tech_skills_count,
        projects_count=projects_count,
        certifications_count=certifications_count,
    )

    # 4. Job Matching Insights (Job matching is ephemeral; not persisted in DB)
    job_matching_insights = JobMatchInsights(
        has_persisted_matches=False,
        total_matches_count=0,
        latest_match_score=None,
        latest_matched_role=None,
        status_message="No job matches yet",
    )

    # 5. Skill Gap Insights
    reports = (
        db.query(SkillGapReport)
        .filter(SkillGapReport.career_profile_id == profile.id)
        .order_by(SkillGapReport.created_at.desc())
        .all()
    )

    if reports:
        latest_rep = reports[0]
        skill_gap_insights = SkillGapInsights(
            has_report=True,
            total_reports_count=len(reports),
            latest_target_role=latest_rep.target_role,
            latest_role_title=latest_rep.role_title or latest_rep.target_role.replace("_", " ").title(),
            latest_score=round(latest_rep.overall_score, 1) if latest_rep.overall_score is not None else None,
            required_coverage_pct=round(latest_rep.required_coverage_percentage, 1) if latest_rep.required_coverage_percentage is not None else None,
            matched_skills_count=latest_rep.matched_required_skills_count or 0,
            related_skills_count=latest_rep.related_required_skills_count or 0,
            missing_skills_count=latest_rep.missing_required_skills_count or 0,
            latest_analyzed_at=latest_rep.created_at,
            status_message=f"Analyzed for {latest_rep.role_title or latest_rep.target_role}",
        )
    else:
        skill_gap_insights = SkillGapInsights(
            has_report=False,
            total_reports_count=0,
            latest_target_role=None,
            latest_role_title=None,
            latest_score=None,
            required_coverage_pct=None,
            matched_skills_count=0,
            related_skills_count=0,
            missing_skills_count=0,
            latest_analyzed_at=None,
            status_message="Not analyzed yet",
        )

    # 6. Learning Roadmap Insights
    roadmaps = (
        db.query(LearningRoadmap)
        .filter(LearningRoadmap.career_profile_id == profile.id)
        .order_by(LearningRoadmap.created_at.desc())
        .all()
    )

    if roadmaps:
        active_rm = roadmaps[0]
        try:
            progress_data = roadmap_service.get_roadmap_progress(db, profile.id, active_rm.id)
            progress_pct = float(progress_data.get("progress_percentage", 0.0))
            completed_topics = int(progress_data.get("completed_topics", 0))
            total_topics = int(progress_data.get("total_topics", 0))
            remaining_hours = float(progress_data.get("estimated_hours_remaining", 0.0))
            next_topic = progress_data.get("next_recommended_topic")
        except Exception as exc:
            logger.warning("Failed to calculate detailed roadmap progress for %s: %s", active_rm.id, exc)
            progress_pct = float(active_rm.progress_percentage or 0.0)
            completed_topics = active_rm.completed_topics_count or 0
            total_topics = active_rm.total_topics_count or 0
            remaining_hours = float(active_rm.total_estimated_hours or 0.0)
            next_topic = None

        learning_roadmap_insights = LearningRoadmapInsights(
            has_roadmap=True,
            roadmap_id=active_rm.id,
            title=active_rm.title,
            target_role=active_rm.target_role,
            status=active_rm.status,
            progress_percentage=round(progress_pct, 1),
            completed_topics_count=completed_topics,
            total_topics_count=total_topics,
            remaining_hours=round(remaining_hours, 1),
            weekly_study_hours=active_rm.weekly_study_hours or 0,
            next_recommended_topic=next_topic,
            status_message=f"{round(progress_pct)}% completed",
        )
    else:
        learning_roadmap_insights = LearningRoadmapInsights(
            has_roadmap=False,
            roadmap_id=None,
            title=None,
            target_role=None,
            status=None,
            progress_percentage=0.0,
            completed_topics_count=0,
            total_topics_count=0,
            remaining_hours=0.0,
            weekly_study_hours=0,
            next_recommended_topic=None,
            status_message="No roadmap generated yet",
        )

    # 7. Mock Interview Insights
    sessions = (
        db.query(InterviewSession)
        .filter(InterviewSession.career_profile_id == profile.id)
        .order_by(InterviewSession.created_at.desc())
        .all()
    )

    completed_sessions = [
        s for s in sessions if s.status == "completed" and s.overall_score is not None
    ]

    if completed_sessions:
        scores = [s.overall_score for s in completed_sessions]
        avg_score = round(sum(scores) / len(scores), 1)
        best_score = round(max(scores), 1)
        latest_date = completed_sessions[0].completed_at or completed_sessions[0].created_at
        latest_role = completed_sessions[0].role_title or completed_sessions[0].target_role

        mock_interview_insights = MockInterviewInsights(
            has_interviews=True,
            total_completed_interviews=len(completed_sessions),
            average_score=avg_score,
            best_score=best_score,
            latest_interview_date=latest_date,
            most_recent_status=sessions[0].status if sessions else "completed",
            latest_target_role=latest_role,
            status_message=f"{len(completed_sessions)} interview completed",
        )
    else:
        mock_interview_insights = MockInterviewInsights(
            has_interviews=False,
            total_completed_interviews=0,
            average_score=None,
            best_score=None,
            latest_interview_date=None,
            most_recent_status=sessions[0].status if sessions else None,
            latest_target_role=None,
            status_message="No interviews completed yet",
        )

    return DashboardInsightsResponse(
        career_profile=profile_summary,
        resume=resume_insights,
        job_matching=job_matching_insights,
        skill_gap=skill_gap_insights,
        learning_roadmap=learning_roadmap_insights,
        mock_interview=mock_interview_insights,
    )

