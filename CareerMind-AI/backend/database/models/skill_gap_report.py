"""
SkillGapReport entity representing persistent skill gap analysis results against a benchmark role.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class SkillGapReport(Base):
    """
    Persistent record of a skill gap assessment comparing a specific resume
    against a standard or custom career role benchmark.
    """

    __tablename__ = "skill_gap_reports"

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
    target_role: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    role_title: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    benchmark_version: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="1.0.0",
    )
    overall_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    required_coverage_percentage: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    preferred_coverage_percentage: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    total_required_skills: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    matched_required_skills_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    related_required_skills_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    missing_required_skills_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    total_preferred_skills: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    matched_preferred_skills_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    related_preferred_skills_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    missing_preferred_skills_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    matched_skills: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    related_skills: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    missing_required_skills: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    missing_preferred_skills: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    category_breakdown: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    analysis_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="completed",  # 'completed', 'insufficient_benchmark', 'no_candidate_skills'
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
        back_populates="skill_gap_reports",
    )
    resume_record: Mapped["ResumeRecord"] = relationship(
        "ResumeRecord",
        back_populates="skill_gap_reports",
    )
    learning_roadmaps: Mapped[list["LearningRoadmap"]] = relationship(
        "LearningRoadmap",
        back_populates="skill_gap_report",
        cascade="all, delete-orphan",
    )
    interview_sessions: Mapped[list["InterviewSession"]] = relationship(
        "InterviewSession",
        back_populates="skill_gap_report",
    )

    @property
    def resume_name(self) -> str | None:
        if self.resume_record:
            return self.resume_record.display_name or self.resume_record.original_filename
        return None
