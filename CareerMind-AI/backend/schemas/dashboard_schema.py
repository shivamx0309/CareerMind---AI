"""
Pydantic schemas for Centralized Dashboard Career Insights (Phase 6).

Provides structured, explainable response contracts representing actual saved
candidate telemetry across:
- Profile overview
- Resume status and extracted competencies
- Job matching status
- Skill gap analysis reports
- Personalized learning roadmap progress
- AI mock interview performance history
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class CareerProfileSummary(BaseModel):
    """Essential candidate profile attributes for dashboard header & profile card."""
    profile_id: str = Field(..., description="Unique career profile UUID")
    user_id: str = Field(..., description="Local user ID")
    full_name: str = Field(..., description="Full candidate name")
    career_status: str = Field(..., description="Candidate status e.g. Fresher, Working Professional")
    primary_target_role: str = Field(..., description="Target role name e.g. SDE, Data Analyst")
    highest_education: Optional[str] = Field(None, description="e.g. Bachelor's Degree")
    degree: Optional[str] = Field(None, description="Specialization or major e.g. CSE")
    institution: Optional[str] = Field(None, description="Educational institution")
    graduation_year: Optional[int] = Field(None, description="Year of graduation")
    preferred_job_type: Optional[str] = Field(None, description="Full-time, Part-time, Internship")
    preferred_work_mode: Optional[str] = Field(None, description="Remote, Hybrid, On-site")
    preferred_locations: List[str] = Field(default_factory=list, description="Target job locations")
    total_experience_summary: str = Field("Fresher", description="Reliable experience summary or Fresher")
    technical_skills_count: int = Field(0, description="Total extracted technical skills")
    projects_count: int = Field(0, description="Total verified projects from resume")
    certifications_count: int = Field(0, description="Total certifications from resume")

    model_config = ConfigDict(from_attributes=True)


class ResumeInsights(BaseModel):
    """Real data metrics extracted from the candidate's active/default resume."""
    has_resume: bool = Field(..., description="Whether a resume record exists")
    status: str = Field(..., description="Status: 'Not Uploaded', 'Uploaded', 'Parsed', 'Parsing Failed'")
    resume_id: Optional[str] = Field(None, description="Database UUID of the active resume")
    file_id: Optional[str] = Field(None, description="32-hex file identifier")
    display_name: Optional[str] = Field(None, description="Filename or clean display label")
    is_default: bool = Field(False, description="Whether this resume is designated as default")
    total_skills: int = Field(0, description="Count of distinct skills extracted from resume")
    education_count: int = Field(0, description="Count of education history entries")
    experience_count: int = Field(0, description="Count of professional experience entries")
    project_count: int = Field(0, description="Count of technical projects")
    certification_count: int = Field(0, description="Count of certifications")
    uploaded_at: Optional[datetime] = Field(None, description="Date of upload")
    last_parsed_at: Optional[datetime] = Field(None, description="Date of completed parsing")
    top_skills: List[str] = Field(default_factory=list, description="Top extracted skills for quick preview")

    model_config = ConfigDict(from_attributes=True)


class JobMatchInsights(BaseModel):
    """Job matching telemetry (only reflects persisted analyses; no fabricated counts)."""
    has_persisted_matches: bool = Field(False, description="Whether persisted job matching records exist")
    total_matches_count: int = Field(0, description="Count of persisted job matching analyses")
    latest_match_score: Optional[float] = Field(None, description="Latest job match percentage score")
    latest_matched_role: Optional[str] = Field(None, description="Latest matched job title")
    status_message: str = Field("No job matches yet", description="Human-readable state message")

    model_config = ConfigDict(from_attributes=True)


class SkillGapInsights(BaseModel):
    """Telemetry from actual persisted SkillGapReport records."""
    has_report: bool = Field(False, description="Whether at least one skill gap analysis exists")
    total_reports_count: int = Field(0, description="Total count of historical skill gap reports")
    latest_target_role: Optional[str] = Field(None, description="Target role ID e.g. 'data_analyst'")
    latest_role_title: Optional[str] = Field(None, description="Display title e.g. 'Data Analyst'")
    latest_score: Optional[float] = Field(None, description="Explainable benchmark match score (0-100)")
    required_coverage_pct: Optional[float] = Field(None, description="Required skills coverage percentage")
    matched_skills_count: int = Field(0, description="Count of benchmark required skills matched")
    related_skills_count: int = Field(0, description="Count of related skills identified")
    missing_skills_count: int = Field(0, description="Count of critical missing benchmark skills")
    latest_analyzed_at: Optional[datetime] = Field(None, description="Timestamp of latest analysis")
    status_message: str = Field("Not analyzed yet", description="Human-readable state message")

    model_config = ConfigDict(from_attributes=True)


class LearningRoadmapInsights(BaseModel):
    """Telemetry from active LearningRoadmap and progress engine."""
    has_roadmap: bool = Field(False, description="Whether an active learning roadmap exists")
    roadmap_id: Optional[str] = Field(None, description="Roadmap UUID")
    title: Optional[str] = Field(None, description="Roadmap display title")
    target_role: Optional[str] = Field(None, description="Target role identifier")
    status: Optional[str] = Field(None, description="Roadmap status e.g. 'in_progress', 'completed'")
    progress_percentage: float = Field(0.0, description="Authoritative progress percentage (0-100)")
    completed_topics_count: int = Field(0, description="Completed topics count")
    total_topics_count: int = Field(0, description="Total roadmap topics count")
    remaining_hours: float = Field(0.0, description="Estimated study hours remaining")
    weekly_study_hours: int = Field(0, description="Planned weekly study commitment")
    next_recommended_topic: Optional[Dict[str, Any]] = Field(None, description="Next pending topic to learn")
    status_message: str = Field("No roadmap generated yet", description="Human-readable status")

    model_config = ConfigDict(from_attributes=True)


class MockInterviewInsights(BaseModel):
    """Telemetry from completed AI Mock Interview sessions and reports."""
    has_interviews: bool = Field(False, description="Whether at least one completed interview exists")
    total_completed_interviews: int = Field(0, description="Count of completed interview sessions")
    average_score: Optional[float] = Field(None, description="Average overall score across completed sessions")
    best_score: Optional[float] = Field(None, description="Highest score across completed sessions")
    latest_interview_date: Optional[datetime] = Field(None, description="Date of latest interview completion")
    most_recent_status: Optional[str] = Field(None, description="Status of most recent session")
    latest_target_role: Optional[str] = Field(None, description="Role title of latest interview")
    status_message: str = Field("No interviews completed yet", description="Human-readable status")

    model_config = ConfigDict(from_attributes=True)


class DashboardInsightsResponse(BaseModel):
    """Consolidated single-request response contract for the CareerMind AI Dashboard."""
    career_profile: CareerProfileSummary
    resume: ResumeInsights
    job_matching: JobMatchInsights
    skill_gap: SkillGapInsights
    learning_roadmap: LearningRoadmapInsights
    mock_interview: MockInterviewInsights

    model_config = ConfigDict(from_attributes=True)

