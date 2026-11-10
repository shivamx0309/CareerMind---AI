"""
Pydantic schemas for the Personalized Learning Roadmap Engine (Phase 4).
Defines contracts for generation requests, skills, topics, resources, milestones,
progress tracking, and persisted roadmaps.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class RoadmapGenerateRequest(BaseModel):
    """Payload to generate a personalized learning roadmap."""

    skill_gap_report_id: str = Field(..., description="UUID of the saved SkillGapReport")
    weekly_study_hours: Optional[int] = Field(
        default=10,
        ge=1,
        le=60,
        description="Weekly study commitment in hours (default: 10, supported presets: 5, 10, 15, 20 or custom)",
    )
    title: Optional[str] = Field(default=None, description="Custom title for the roadmap")


class LearningResourceResponse(BaseModel):
    """Verified free learning resource metadata."""

    id: str
    roadmap_topic_id: str
    skill_name: str
    title: str
    url: str
    provider: str
    resource_type: str
    is_free: bool = True
    difficulty: str
    estimated_minutes: int

    model_config = ConfigDict(from_attributes=True)


class RoadmapTopicResponse(BaseModel):
    """Granular topic unit within a roadmap skill."""

    id: str
    roadmap_skill_id: str
    topic_name: str
    sequence_order: int
    estimated_hours: float
    status: str = "not_started"  # not_started, in_progress, completed
    completed_at: Optional[datetime] = None
    resources: List[LearningResourceResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class PracticalProject(BaseModel):
    """Practical hands-on exercise or mini-project to validate skill mastery."""

    title: str
    description: str
    deliverables: List[str] = Field(default_factory=list)


class RoadmapSkillResponse(BaseModel):
    """Skill module within the personalized learning roadmap."""

    id: str
    roadmap_id: str
    skill_name: str
    category: str
    priority: str  # high, medium, low
    importance: str  # required, preferred
    gap_type: str  # missing_required, related_required, missing_preferred
    sequence_order: int
    estimated_hours: float
    rationale: str
    prerequisites: List[str] = Field(default_factory=list)
    status: str = "not_started"  # not_started, in_progress, completed
    practical_project: Optional[Dict[str, Any]] = None
    topics: List[RoadmapTopicResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class RoadmapMilestoneResponse(BaseModel):
    """Sequential weekly milestone tracking overall curriculum progress."""

    id: str
    roadmap_id: str
    title: str
    description: str
    sequence_order: int
    week_number: int
    status: str = "pending"  # pending, in_progress, completed
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class LearningRoadmapResponse(BaseModel):
    """Full personalized learning roadmap entity with nested skills, topics, and milestones."""

    id: str
    career_profile_id: str
    resume_record_id: str
    skill_gap_report_id: str
    target_role: str
    role_title: str
    title: str
    weekly_study_hours: int
    total_estimated_hours: float
    total_weeks: int
    completed_topics_count: int
    total_topics_count: int
    progress_percentage: float
    status: str  # in_progress, completed, archived
    weekly_schedule: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    skills: List[RoadmapSkillResponse] = Field(default_factory=list)
    milestones: List[RoadmapMilestoneResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class LearningRoadmapSummaryResponse(BaseModel):
    """Lightweight summary of a learning roadmap for listing views."""

    id: str
    career_profile_id: str
    resume_record_id: str
    skill_gap_report_id: str
    target_role: str
    role_title: str
    title: str
    weekly_study_hours: int
    total_estimated_hours: float
    total_weeks: int
    completed_topics_count: int
    total_topics_count: int
    progress_percentage: float
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TopicStatusUpdateRequest(BaseModel):
    """Payload to update completion status of a topic."""

    status: str = Field(..., pattern="^(not_started|in_progress|completed)$")


class SkillStatusUpdateRequest(BaseModel):
    """Payload to update completion status of an entire skill module."""

    status: str = Field(..., pattern="^(not_started|in_progress|completed)$")


class MilestoneStatusUpdateRequest(BaseModel):
    """Payload to update milestone status."""

    status: str = Field(..., pattern="^(pending|in_progress|completed)$")


class RoadmapProgressResponse(BaseModel):
    """Detailed progress tracking telemetry for a learning roadmap."""

    roadmap_id: str
    total_skills: int
    completed_skills: int
    total_topics: int
    completed_topics: int
    progress_percentage: float
    estimated_hours_remaining: float
    current_week: int
    status: str
    next_recommended_topic: Optional[Dict[str, Any]] = None

