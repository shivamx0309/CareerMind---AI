"""
InterviewAnswer model representing a candidate's answer submitted for a question.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
import uuid

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    from database.models.interview_session_question import InterviewSessionQuestion
    from database.models.interview_evaluation import InterviewEvaluation


class InterviewAnswer(Base):
    """
    Candidate's submitted response text to a specific session question.
    """

    __tablename__ = "interview_answers"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    session_question_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("interview_session_questions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    answer_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    session_question: Mapped["InterviewSessionQuestion"] = relationship(
        "InterviewSessionQuestion",
        back_populates="answer",
    )
    evaluation: Mapped[Optional["InterviewEvaluation"]] = relationship(
        "InterviewEvaluation",
        back_populates="answer",
        uselist=False,
        cascade="all, delete-orphan",
    )

