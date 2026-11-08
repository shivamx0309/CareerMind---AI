"""
ResumeRecord entity representing an independent resume file in the user's resume library.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Index, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class ResumeRecord(Base):
    """
    Metadata and pointer for an uploaded resume PDF stored on the filesystem.
    Supports multiple resumes per profile (active default, renaming, replacement, deletion).
    """

    __tablename__ = "resume_records"

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
    file_id: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        nullable=False,
        index=True,  # Matches data/uploads/{file_id}.pdf
    )
    display_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        default="Default Resume",  # User-editable title for renaming
    )
    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,  # Server-derived and validated path
    )
    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    upload_status: Mapped[str] = mapped_column(
        String(50),
        default="completed",
        nullable=False,  # 'completed', 'failed'
    )
    extraction_status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,  # 'pending', 'completed', 'no_text_found', 'failed'
    )
    parsing_status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,  # 'pending', 'completed', 'failed'
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
    last_parsed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    career_profile: Mapped["CareerProfile"] = relationship(
        "CareerProfile",
        back_populates="resume_records",
    )
    resume_profile: Mapped["ResumeProfile"] = relationship(
        "ResumeProfile",
        back_populates="resume_record",
        uselist=False,
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        # Enforces at most one default resume per career profile at the database level
        Index(
            "uq_profile_default_resume",
            "career_profile_id",
            unique=True,
            sqlite_where=text("is_default = 1"),
        ),
    )
