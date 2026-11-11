"""
Unit tests for CareerMind AI Centralized Dashboard Career Insights Service (Phase 6).
"""

import pytest
from database.session import SessionLocal
from database.models import (
    CareerProfile,
    ResumeRecord,
    ResumeProfile,
    ResumeSkill,
    SkillGapReport,
    LearningRoadmap,
    InterviewSession,
)
from services.dashboard_service import get_dashboard_insights
from schemas.dashboard_schema import DashboardInsightsResponse


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_get_dashboard_insights_returns_valid_schema(db_session):
    """Verify get_dashboard_insights returns a well-formed DashboardInsightsResponse with real data."""
    insights = get_dashboard_insights(db_session, user_id="local_user")
    assert isinstance(insights, DashboardInsightsResponse)

    # 1. Career Profile
    assert insights.career_profile is not None
    assert insights.career_profile.user_id == "local_user"
    assert insights.career_profile.full_name == "Shivam Kumar Singh"
    assert insights.career_profile.primary_target_role == "SDE"
    assert insights.career_profile.technical_skills_count >= 0

    # 2. Resume Insights
    assert insights.resume is not None
    assert insights.resume.has_resume is True
    assert insights.resume.status in ["Parsed", "Uploaded", "Not Uploaded", "Parsing Failed"]
    if insights.resume.status == "Parsed":
        assert insights.resume.total_skills > 0
        assert isinstance(insights.resume.top_skills, list)

    # 3. Job Match Insights
    assert insights.job_matching is not None
    assert insights.job_matching.has_persisted_matches is False
    assert insights.job_matching.total_matches_count == 0
    assert insights.job_matching.status_message == "No job matches yet"

    # 4. Skill Gap Insights
    assert insights.skill_gap is not None
    if insights.skill_gap.has_report:
        assert insights.skill_gap.total_reports_count > 0
        assert insights.skill_gap.latest_score is not None
        assert 0.0 <= insights.skill_gap.latest_score <= 100.0
    else:
        assert insights.skill_gap.status_message == "Not analyzed yet"

    # 5. Learning Roadmap Insights
    assert insights.learning_roadmap is not None
    if insights.learning_roadmap.has_roadmap:
        assert 0.0 <= insights.learning_roadmap.progress_percentage <= 100.0
        assert insights.learning_roadmap.total_topics_count >= 0
    else:
        assert insights.learning_roadmap.status_message == "No roadmap generated yet"

    # 6. Mock Interview Insights
    assert insights.mock_interview is not None
    if insights.mock_interview.has_interviews:
        assert insights.mock_interview.total_completed_interviews > 0
        assert insights.mock_interview.average_score is not None
        assert 0.0 <= insights.mock_interview.average_score <= 100.0
    else:
        assert insights.mock_interview.status_message == "No interviews completed yet"


def test_dashboard_accuracy_rules(db_session):
    """Verify that values in dashboard insights match exact database state and do not fabricate data."""
    insights = get_dashboard_insights(db_session, user_id="local_user")

    profile = db_session.query(CareerProfile).filter(CareerProfile.user_id == "local_user").first()
    assert insights.career_profile.profile_id == profile.id
    assert insights.career_profile.full_name == profile.full_name

    # Check SkillGapReports count matches DB
    db_reports_count = db_session.query(SkillGapReport).filter(SkillGapReport.career_profile_id == profile.id).count()
    assert insights.skill_gap.total_reports_count == db_reports_count

    # Check Completed Interviews count matches DB
    db_completed_interviews = (
        db_session.query(InterviewSession)
        .filter(InterviewSession.career_profile_id == profile.id, InterviewSession.status == "completed")
        .count()
    )
    assert insights.mock_interview.total_completed_interviews == db_completed_interviews

    # Check active resume skills count matches DB
    if insights.resume.has_resume and insights.resume.resume_id:
        active_record = db_session.query(ResumeRecord).filter(ResumeRecord.id == insights.resume.resume_id).first()
        if active_record and active_record.resume_profile:
            expected_skills_count = len(active_record.resume_profile.skills)
            assert insights.resume.total_skills == expected_skills_count
            assert insights.career_profile.technical_skills_count == expected_skills_count
