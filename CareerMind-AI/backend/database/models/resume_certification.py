"""
ResumeCertification entity representing licenses and certificates extracted from a specific resume.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class ResumeCertification(Base):
    """
    Candidate certification or accredited course extracted from a specific resume.
    """

    __tablename__ = "resume_certifications"

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
    certification_name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )
    issuing_organization: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )
    issue_date: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    credential_url: Mapped[str | None] = mapped_column(
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
        back_populates="certifications",
    )

