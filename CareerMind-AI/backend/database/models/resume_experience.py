"""
ResumeExperience entity representing professional employment or internships extracted from a specific resume.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class ResumeExperience(Base):
    """
    Work experience or internship record extracted from a specific resume.
    """

    __tablename__ = "resume_experiences"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    resume_profile_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("resume_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_title: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )
    company: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )
    employment_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,  # e.g., 'Full-time', 'Internship', 'Contract'
    )
    location: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    start_date: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    end_date: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    technologies: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    resume_profile: Mapped["ResumeProfile"] = relationship(
        "ResumeProfile",
        back_populates="experiences",
    )

