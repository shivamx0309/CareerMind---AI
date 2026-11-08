"""
ResumeSkill entity representing categorized technical competencies extracted from a specific resume.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class ResumeSkill(Base):
    """
    Extracted technical skill tied to a specific resume profile.
    Maintains categorization matching the 10 TechnicalSkills categories.
    """

    __tablename__ = "resume_skills"

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
    skill_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,  # e.g., 'programming_languages', 'backend', 'databases', etc.
    )
    confidence: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    resume_profile: Mapped["ResumeProfile"] = relationship(
        "ResumeProfile",
        back_populates="skills",
    )
