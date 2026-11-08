"""
CareerGoal entity representing candidate target roles, job types, and timeline.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class CareerGoal(Base):
    """
    Candidate target roles, compensation preferences, and search timeline.
    1-to-1 relationship with CareerProfile.
    """

    __tablename__ = "career_goals"

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
    target_roles: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    preferred_locations: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    preferred_work_modes: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    preferred_job_types: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    expected_salary: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    job_search_timeline: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,  # e.g., 'Immediately', '1-3 months', 'Exploring'
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
        back_populates="career_goals",
    )

