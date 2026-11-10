"""
RoadmapMilestone entity representing weekly sequential milestones in a learning curriculum.
"""

from datetime import datetime
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    from database.models.learning_roadmap import LearningRoadmap


class RoadmapMilestone(Base):
    """
    Weekly milestone outlining practical achievements, study goals,
    and completion status across the roadmap.
    """

    __tablename__ = "roadmap_milestones"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    roadmap_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("learning_roadmaps.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )
    sequence_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    week_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="pending",  # pending, in_progress, completed
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    roadmap: Mapped["LearningRoadmap"] = relationship(
        "LearningRoadmap",
        back_populates="milestones",
    )

