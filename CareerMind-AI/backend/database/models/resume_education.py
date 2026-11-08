"""
ResumeEducation entity representing educational qualifications extracted from a specific resume.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class ResumeEducation(Base):
    """
    Candidate educational qualification extracted from a specific resume.
    """

    __tablename__ = "resume_educations"

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
    degree: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )
    institution: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )
    specialization: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )
    start_year: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )
    end_year: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )
    grade_or_cgpa: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    resume_profile: Mapped["ResumeProfile"] = relationship(
        "ResumeProfile",
        back_populates="educations",
    )

