"""
LearningRoadmap entity representing a personalized, structured learning curriculum.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    from database.models.career_profile import CareerProfile
    from database.models.resume_record import ResumeRecord
    from database.models.skill_gap_report import SkillGapReport
    from database.models.roadmap_skill import RoadmapSkill
    from database.models.roadmap_milestone import RoadmapMilestone


class LearningRoadmap(Base):
    """
    Persistent record of an actionable learning roadmap generated from
    a SkillGapReport with weekly study schedule and progress telemetry.
    """

    __tablename__ = "learning_roadmaps"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    career_profile_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("career_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    resume_record_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("resume_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_gap_report_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("skill_gap_reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_role: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    role_title: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    weekly_study_hours: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=10,
    )
    total_estimated_hours: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    total_weeks: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )
    completed_topics_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    total_topics_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    progress_percentage: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="in_progress",  # in_progress, completed, archived
    )
    weekly_schedule: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    career_profile: Mapped["CareerProfile"] = relationship(
        "CareerProfile",
        back_populates="learning_roadmaps",
    )
    resume_record: Mapped["ResumeRecord"] = relationship(
        "ResumeRecord",
        back_populates="learning_roadmaps",
    )
    skill_gap_report: Mapped["SkillGapReport"] = relationship(
        "SkillGapReport",
        back_populates="learning_roadmaps",
    )
    skills: Mapped[list["RoadmapSkill"]] = relationship(
        "RoadmapSkill",
        back_populates="roadmap",
        cascade="all, delete-orphan",
        order_by="RoadmapSkill.sequence_order",
    )
    milestones: Mapped[list["RoadmapMilestone"]] = relationship(
        "RoadmapMilestone",
        back_populates="roadmap",
        cascade="all, delete-orphan",
        order_by="RoadmapMilestone.sequence_order",
    )

