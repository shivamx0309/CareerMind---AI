"""
InterviewReport model representing a comprehensive assessment report for a completed session.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import String, Integer, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    from database.models.interview_session import InterviewSession


class InterviewReport(Base):
    """
    Final performance assessment report for a completed interview session,
    providing category-level breakdowns, strengths, weak areas, and revision topics.
    """

    __tablename__ = "interview_reports"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    overall_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,  # 0.0 to 100.0
    )
    questions_attempted: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    total_questions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    average_answer_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    category_scores: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    strong_areas: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    weak_areas: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    frequently_missed_concepts: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    recommended_topics: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    actionable_feedback: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    performance_summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    session: Mapped["InterviewSession"] = relationship(
        "InterviewSession",
        back_populates="report",
    )

