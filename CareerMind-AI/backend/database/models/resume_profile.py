"""
ResumeProfile entity representing candidate personal details parsed from a specific resume.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class ResumeProfile(Base):
    """
    Candidate contact and personal information extracted from a specific resume.
    1-to-1 relationship with ResumeRecord.
    """

    __tablename__ = "resume_profiles"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    resume_record_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("resume_records.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    full_name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )
    email: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )
    phone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    linkedin: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    github: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    portfolio: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    location: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )
    professional_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    achievements: Mapped[list] = mapped_column(
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
    resume_record: Mapped["ResumeRecord"] = relationship(
        "ResumeRecord",
        back_populates="resume_profile",
    )
    skills: Mapped[list["ResumeSkill"]] = relationship(
        "ResumeSkill",
        back_populates="resume_profile",
        cascade="all, delete-orphan",
    )
    educations: Mapped[list["ResumeEducation"]] = relationship(
        "ResumeEducation",
        back_populates="resume_profile",
        cascade="all, delete-orphan",
    )
    experiences: Mapped[list["ResumeExperience"]] = relationship(
        "ResumeExperience",
        back_populates="resume_profile",
        cascade="all, delete-orphan",
    )
    projects: Mapped[list["ResumeProject"]] = relationship(
        "ResumeProject",
        back_populates="resume_profile",
        cascade="all, delete-orphan",
    )
    certifications: Mapped[list["ResumeCertification"]] = relationship(
        "ResumeCertification",
        back_populates="resume_profile",
        cascade="all, delete-orphan",
    )
