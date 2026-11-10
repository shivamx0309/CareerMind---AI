"""
InterviewSession model representing a candidate's mock interview session.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
import uuid

from sqlalchemy import String, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    from database.models.career_profile import CareerProfile
    from database.models.resume_record import ResumeRecord
    from database.models.skill_gap_report import SkillGapReport
    from database.models.interview_session_question import InterviewSessionQuestion
    from database.models.interview_report import InterviewReport


class InterviewSession(Base):
    """
    Persistent interview session tracking configuration, status, active question index,
    and references to selected resume or skill gap reports.
    """

    __tablename__ = "interview_sessions"

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
    resume_record_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("resume_records.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    skill_gap_report_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("skill_gap_reports.id", ondelete="SET NULL"),
        nullable=True,
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
    interview_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="technical",  # technical, behavioral, project, mixed
    )
    difficulty: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="intermediate",  # beginner, intermediate, advanced
    )
    total_questions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5,
    )
    current_question_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="in_progress",  # pending, in_progress, completed, abandoned
    )
    overall_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    performance_summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
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
        back_populates="interview_sessions",
    )
    resume_record: Mapped[Optional["ResumeRecord"]] = relationship(
        "ResumeRecord",
        back_populates="interview_sessions",
    )
    skill_gap_report: Mapped[Optional["SkillGapReport"]] = relationship(
        "SkillGapReport",
        back_populates="interview_sessions",
    )
    questions: Mapped[List["InterviewSessionQuestion"]] = relationship(
        "InterviewSessionQuestion",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="InterviewSessionQuestion.sequence_order",
    )
    report: Mapped[Optional["InterviewReport"]] = relationship(
        "InterviewReport",
        back_populates="session",
        uselist=False,
        cascade="all, delete-orphan",
    )

