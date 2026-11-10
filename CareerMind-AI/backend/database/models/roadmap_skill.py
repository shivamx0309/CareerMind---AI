"""
RoadmapSkill entity representing an individual skill within a personalized roadmap.
"""

from typing import TYPE_CHECKING
import uuid

from sqlalchemy import String, Integer, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    from database.models.learning_roadmap import LearningRoadmap
    from database.models.roadmap_topic import RoadmapTopic


class RoadmapSkill(Base):
    """
    Skill module assigned to a learning roadmap with priority, prerequisite sequence,
    estimated study hours, rationale, practical project, and completion status.
    """

    __tablename__ = "roadmap_skills"

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
    skill_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="medium",  # high, medium, low
    )
    importance: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="required",  # required, preferred
    )
    gap_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="missing_required",  # missing_required, related_required, missing_preferred
    )
    sequence_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    estimated_hours: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    rationale: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )
    prerequisites: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="not_started",  # not_started, in_progress, completed
    )
    practical_project: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # Relationships
    roadmap: Mapped["LearningRoadmap"] = relationship(
        "LearningRoadmap",
        back_populates="skills",
    )
    topics: Mapped[list["RoadmapTopic"]] = relationship(
        "RoadmapTopic",
        back_populates="roadmap_skill",
        cascade="all, delete-orphan",
        order_by="RoadmapTopic.sequence_order",
    )

