"""
LearningPreference entity representing candidate learning habits and interview prep focus.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class LearningPreference(Base):
    """
    Candidate learning objectives, study hours, and interview goals.
    1-to-1 relationship with CareerProfile.
    """

    __tablename__ = "learning_preferences"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    career_profile_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("career_profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    learning_objective: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    daily_learning_hours: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    preferred_language: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    interview_preparation_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,  # e.g., 'System Design', 'Coding', 'Behavioral'
    )
    preferred_learning_style: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,  # e.g., 'Hands-on projects', 'Video courses', 'Documentation'
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

    career_profile: Mapped["CareerProfile"] = relationship(
        "CareerProfile",
        back_populates="learning_preferences",
    )

