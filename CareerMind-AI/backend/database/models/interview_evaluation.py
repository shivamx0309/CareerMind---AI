"""
InterviewEvaluation model representing structured feedback and scores for an answer.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import String, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    from database.models.interview_answer import InterviewAnswer


class InterviewEvaluation(Base):
    """
    Detailed rubric-based evaluation scores, identified/missing concepts,
    strengths, and actionable suggestions for a submitted answer.
    """

    __tablename__ = "interview_evaluations"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    answer_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("interview_answers.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    overall_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,  # 0.0 to 100.0
    )
    relevance_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,  # 0.0 to 100.0
    )
    concept_coverage_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,  # 0.0 to 100.0
    )
    completeness_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,  # 0.0 to 100.0
    )
    structure_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,  # 0.0 to 100.0
    )
    identified_concepts: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    missing_concepts: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    strengths: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    improvement_suggestions: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    evaluator_method: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="deterministic_rubric_v1",
    )
    feedback_rationale: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    answer: Mapped["InterviewAnswer"] = relationship(
        "InterviewAnswer",
        back_populates="evaluation",
    )

