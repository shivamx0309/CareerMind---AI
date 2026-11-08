"""
ResumeProject entity representing portfolio projects extracted from a specific resume.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class ResumeProject(Base):
    """
    Candidate project record extracted from a specific resume.
    """

    __tablename__ = "resume_projects"

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
    project_name: Mapped[str | None] = mapped_column(
        String(150),
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
    project_url: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    resume_profile: Mapped["ResumeProfile"] = relationship(
        "ResumeProfile",
        back_populates="projects",
    )

