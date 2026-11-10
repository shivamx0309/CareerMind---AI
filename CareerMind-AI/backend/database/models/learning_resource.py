"""
LearningResource entity representing a curated free resource for a topic.
"""

from typing import TYPE_CHECKING
import uuid

from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    from database.models.roadmap_topic import RoadmapTopic


class LearningResource(Base):
    """
    Curated, verified free learning resource linking to official documentation,
    free tutorials, or interactive platforms.
    """

    __tablename__ = "learning_resources"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    roadmap_topic_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("roadmap_topics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    provider: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Official Documentation",
    )
    resource_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="documentation",  # documentation, tutorial, course, interactive, book
    )
    is_free: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    difficulty: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="beginner",  # beginner, intermediate, advanced
    )
    estimated_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=30,
    )

    # Relationships
    topic: Mapped["RoadmapTopic"] = relationship(
        "RoadmapTopic",
        back_populates="resources",
    )

