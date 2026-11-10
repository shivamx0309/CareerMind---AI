"""
InterviewSessionQuestion model representing a specific question assigned to an interview session.
"""

from typing import TYPE_CHECKING, Optional, List, Dict
import uuid

from sqlalchemy import String, Integer, Float, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    from database.models.interview_session import InterviewSession
    from database.models.interview_answer import InterviewAnswer


class InterviewSessionQuestion(Base):
    """
    Question snapshot assigned to an interview session.
    Stores question text, rubrics, and answer keys. Internal keys remain hidden from
    candidate view prior to answering.
    """

    __tablename__ = "interview_session_questions"

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
    sequence_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    question_bank_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    question_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    interview_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    difficulty: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    relevant_skill: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    expected_concepts: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    suggested_answer_points: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    evaluation_rubric: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    weight: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
    )
    is_answered: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    # Relationships
    session: Mapped["InterviewSession"] = relationship(
        "InterviewSession",
        back_populates="questions",
    )
    answer: Mapped[Optional["InterviewAnswer"]] = relationship(
        "InterviewAnswer",
        back_populates="session_question",
        uselist=False,
        cascade="all, delete-orphan",
    )

