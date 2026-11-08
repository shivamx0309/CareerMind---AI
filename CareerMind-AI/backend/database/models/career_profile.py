"""
CareerProfile entity representing basic user preferences and local identity.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Text, Boolean, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class CareerProfile(Base):
    """
    Core career profile containing user onboarding preferences.
    In the single-user local MVP, this represents the unique active local user.
    """

    __tablename__ = "career_profiles"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        default="local_user",
        index=True,
    )
    full_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    career_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,  # e.g., 'Student', 'Fresher', 'Experienced'
    )
    highest_education: Mapped[str] = mapped_column(
        String(100),
        nullable=False,  # e.g., "Bachelor's", "Master's", "Doctorate", "High School"
    )
    degree: Mapped[str] = mapped_column(
        String(150),
        nullable=False,  # e.g., "B.Tech Computer Science"
    )
    institution: Mapped[str] = mapped_column(
        String(200),
        nullable=False,  # e.g., "Stanford University"
    )
    graduation_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,  # e.g., 2026
    )
    primary_target_role: Mapped[str] = mapped_column(
        String(150),
        nullable=False,  # e.g., "Python Backend Developer"
    )
    preferred_job_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,  # e.g., 'Full-time', 'Part-time', 'Contract', 'Internship'
    )
    preferred_work_mode: Mapped[str] = mapped_column(
        String(50),
        nullable=False,  # e.g., 'Remote', 'Hybrid', 'On-site'
    )
    preferred_locations: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    career_objective: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    onboarding_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
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
    career_goals: Mapped["CareerGoal"] = relationship(
        "CareerGoal",
        back_populates="career_profile",
        uselist=False,
        cascade="all, delete-orphan",
    )
    learning_preferences: Mapped["LearningPreference"] = relationship(
        "LearningPreference",
        back_populates="career_profile",
        uselist=False,
        cascade="all, delete-orphan",
    )
    resume_records: Mapped[list["ResumeRecord"]] = relationship(
        "ResumeRecord",
        back_populates="career_profile",
        cascade="all, delete-orphan",
        order_by="desc(ResumeRecord.created_at)",
    )
