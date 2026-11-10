"""
RoadmapTopic entity representing a granular study topic within a skill.
"""

from datetime import datetime
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    from database.models.roadmap_skill import RoadmapSkill
    from database.models.learning_resource import LearningResource


class RoadmapTopic(Base):
    """
    Topic within a skill with sequence order, estimated study hours, completion state,
    and attached free curated resources.
    """

    __tablename__ = "roadmap_topics"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    roadmap_skill_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("roadmap_skills.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    topic_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    sequence_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    estimated_hours: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=2.0,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="not_started",  # not_started, in_progress, completed
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    roadmap_skill: Mapped["RoadmapSkill"] = relationship(
        "RoadmapSkill",
        back_populates="topics",
    )
    resources: Mapped[list["LearningResource"]] = relationship(
        "LearningResource",
        back_populates="topic",
        cascade="all, delete-orphan",
    )

