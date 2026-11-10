"""
Personalized Learning Roadmap Engine Service.
Orchestrates conversion of SkillGapReports into structured, dependency-ordered,
weekly learning curriculums with progress tracking and persistent database operations.
"""

from datetime import datetime, timezone
import math
from typing import Any, Dict, List, Optional
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models.learning_roadmap import LearningRoadmap
from database.models.roadmap_skill import RoadmapSkill
from database.models.roadmap_topic import RoadmapTopic
from database.models.learning_resource import LearningResource
from database.models.roadmap_milestone import RoadmapMilestone
from database.models.skill_gap_report import SkillGapReport
from database.models.career_profile import CareerProfile
from services.role_benchmark_service import get_role_benchmark
from services.skill_dependency_service import (
    topological_sort_skills,
    get_skill_topics,
    get_skill_practical_project,
    get_skill_prerequisites,
)
from services.learning_resource_catalog import get_resources_for_topic
from services.learning_priority_service import (
    prioritize_skills_for_roadmap,
    PrioritizedSkillItem,
)


class RoadmapServiceError(Exception):
    """Base exception for learning roadmap service errors."""
    pass


class SkillGapReportNotFoundError(RoadmapServiceError):
    """Raised when the specified SkillGapReport is not found."""
    pass


class InvalidReportStateError(RoadmapServiceError):
    """Raised when the SkillGapReport is in an invalid or insufficient state."""
    pass


class RoadmapNotFoundError(RoadmapServiceError):
    """Raised when the specified LearningRoadmap is not found."""
    pass


class RoadmapItemNotFoundError(RoadmapServiceError):
    """Raised when a specific topic, skill, or milestone is not found in the roadmap."""
    pass


def generate_learning_roadmap(
    db: Session,
    career_profile_id: str,
    skill_gap_report_id: str,
    weekly_study_hours: Optional[int] = None,
    custom_title: Optional[str] = None,
) -> LearningRoadmap:
    """
    Generate a personalized, dependency-sequenced learning roadmap from a saved SkillGapReport.

    Parameters:
        db: Active SQLAlchemy database session.
        career_profile_id: ID of the authenticated user's career profile.
        skill_gap_report_id: ID of the saved SkillGapReport to convert.
        weekly_study_hours: Optional weekly study commitment (defaults to user's
                           LearningPreference or 10 hours/week).
        custom_title: Optional title for the roadmap.

    Returns:
        Persisted LearningRoadmap instance with nested skills, topics, resources, and milestones.
    """
    # 1. Fetch & Validate SkillGapReport
    stmt = select(SkillGapReport).where(
        (SkillGapReport.id == skill_gap_report_id)
        & (SkillGapReport.career_profile_id == career_profile_id)
    )
    report = db.execute(stmt).scalar_one_or_none()
    if not report:
        raise SkillGapReportNotFoundError(
            f"Skill gap report '{skill_gap_report_id}' was not found for this career profile."
        )

    if report.analysis_status == "insufficient_benchmark":
        raise InvalidReportStateError(
            "Cannot generate a roadmap from an insufficient benchmark report with 0 required skills."
        )

    # 2. Resolve Weekly Study Commitment
    study_hours = 10
    if weekly_study_hours is not None and weekly_study_hours > 0:
        study_hours = min(max(weekly_study_hours, 1), 60)
    else:
        # Check user's LearningPreference
        career_profile = db.get(CareerProfile, career_profile_id)
        if career_profile and career_profile.learning_preferences:
            daily = career_profile.learning_preferences.daily_learning_hours
            if daily and daily > 0:
                study_hours = int(round(daily * 7))
                study_hours = min(max(study_hours, 1), 60)

    # 3. Build Category Map from Benchmark
    benchmark = get_role_benchmark(report.target_role)
    category_map: Dict[str, str] = {}
    if benchmark:
        for s in benchmark.required_skills + benchmark.preferred_skills:
            category_map[s.skill_name] = s.category

    # 4. Determine Prioritized Skills to Learn
    prioritized_skills: List[PrioritizedSkillItem] = prioritize_skills_for_roadmap(
        report=report,
        category_map=category_map,
    )

    # Extract candidate's already mastered skills from matched_skills
    known_skills = {
        item["skill_name"]
        for item in (report.matched_skills or [])
        if item.get("status") in ("exact_match", "alias_match")
    }

    # If the candidate has 0 gaps (e.g. 100% match), provide advanced specialization modules
    if not prioritized_skills and benchmark:
        for pref in benchmark.preferred_skills[:3]:
            prioritized_skills.append(
                PrioritizedSkillItem(
                    skill_name=pref.skill_name,
                    category=pref.category,
                    priority="medium",
                    importance="preferred",
                    gap_type="missing_preferred",
                    rationale=f"Advanced specialization competency for {benchmark.title}.",
                    prerequisites=get_skill_prerequisites(pref.skill_name),
                )
            )

    # 5. Dependency-Aware Sequencing
    # Partition by priority tier to guarantee high -> medium -> low ordering,
    # while applying topological sorting within each tier respecting dependencies
    high_skills = [p.skill_name for p in prioritized_skills if p.priority == "high"]
    med_skills = [p.skill_name for p in prioritized_skills if p.priority == "medium"]
    low_skills = [p.skill_name for p in prioritized_skills if p.priority == "low"]

    sorted_high = topological_sort_skills(high_skills, known_skills)
    sorted_med = topological_sort_skills(med_skills, known_skills.union(set(sorted_high)))
    sorted_low = topological_sort_skills(low_skills, known_skills.union(set(sorted_high), set(sorted_med)))

    ordered_skill_names = sorted_high + sorted_med + sorted_low
    skill_item_by_name = {p.skill_name: p for p in prioritized_skills}

    # 6. Initialize LearningRoadmap Entity
    roadmap_id = str(uuid.uuid4())
    roadmap_title = custom_title or f"Personalized Learning Roadmap for {report.role_title}"

    roadmap = LearningRoadmap(
        id=roadmap_id,
        career_profile_id=career_profile_id,
        resume_record_id=report.resume_record_id,
        skill_gap_report_id=report.id,
        target_role=report.target_role,
        role_title=report.role_title,
        title=roadmap_title,
        weekly_study_hours=study_hours,
        status="in_progress",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(roadmap)

    # 7. Construct RoadmapSkills and RoadmapTopics
    total_estimated_hours = 0.0
    total_topics_count = 0
    ordered_topics_for_schedule: List[Dict[str, Any]] = []

    for seq_idx, skill_name in enumerate(ordered_skill_names):
        item = skill_item_by_name[skill_name]
        raw_topics = get_skill_topics(skill_name)
        practical_proj = get_skill_practical_project(skill_name)

        skill_hours = sum(float(t["estimated_hours"]) for t in raw_topics)
        total_estimated_hours += skill_hours

        roadmap_skill = RoadmapSkill(
            id=str(uuid.uuid4()),
            roadmap_id=roadmap_id,
            skill_name=skill_name,
            category=item.category,
            priority=item.priority,
            importance=item.importance,
            gap_type=item.gap_type,
            sequence_order=seq_idx + 1,
            estimated_hours=round(skill_hours, 1),
            rationale=item.rationale,
            prerequisites=item.prerequisites,
            status="not_started",
            practical_project=practical_proj,
        )
        db.add(roadmap_skill)

        # Create Topics for this Skill
        for t_idx, t_data in enumerate(raw_topics):
            topic_id = str(uuid.uuid4())
            t_hours = float(t_data["estimated_hours"])
            total_topics_count += 1

            roadmap_topic = RoadmapTopic(
                id=topic_id,
                roadmap_skill_id=roadmap_skill.id,
                topic_name=str(t_data["topic_name"]),
                sequence_order=t_idx + 1,
                estimated_hours=t_hours,
                status="not_started",
            )
            db.add(roadmap_topic)

            ordered_topics_for_schedule.append({
                "topic_id": topic_id,
                "skill_name": skill_name,
                "topic_name": str(t_data["topic_name"]),
                "estimated_hours": t_hours,
            })

            # Curate Verified Free Resources for Topic
            resources_data = get_resources_for_topic(skill_name, str(t_data["topic_name"]))
            for r_data in resources_data:
                learning_resource = LearningResource(
                    id=str(uuid.uuid4()),
                    roadmap_topic_id=topic_id,
                    skill_name=skill_name,
                    title=str(r_data["title"]),
                    url=str(r_data["url"]),
                    provider=str(r_data.get("provider", "Official Documentation")),
                    resource_type=str(r_data.get("resource_type", "documentation")),
                    is_free=bool(r_data.get("is_free", True)),
                    difficulty=str(r_data.get("difficulty", "beginner")),
                    estimated_minutes=int(r_data.get("estimated_minutes", 30)),
                )
                db.add(learning_resource)

    # 8. Compute Duration and Weekly Schedule
    total_weeks = max(1, math.ceil(total_estimated_hours / study_hours))
    roadmap.total_estimated_hours = round(total_estimated_hours, 1)
    roadmap.total_weeks = total_weeks
    roadmap.total_topics_count = total_topics_count
    roadmap.completed_topics_count = 0
    roadmap.progress_percentage = 0.0

    # Distribute topics across sequential weekly milestones
    weekly_schedule: List[Dict[str, Any]] = []
    current_topic_idx = 0
    topics_per_week = max(1, math.ceil(total_topics_count / total_weeks))

    for w in range(1, total_weeks + 1):
        week_topics: List[Dict[str, Any]] = []
        accumulated_hours = 0.0

        while current_topic_idx < len(ordered_topics_for_schedule):
            t_info = ordered_topics_for_schedule[current_topic_idx]
            week_topics.append(t_info)
            accumulated_hours += t_info["estimated_hours"]
            current_topic_idx += 1

            # Once we meet or approach weekly budget, finalize this week
            if accumulated_hours >= study_hours and w < total_weeks:
                break

        distinct_skills = list(dict.fromkeys(t["skill_name"] for t in week_topics))
        skills_str = ", ".join(distinct_skills) if distinct_skills else "Core Synthesis"

        milestone_title = f"Week {w}: {skills_str}"
        milestone_desc = (
            f"Study {len(week_topics)} topics across {skills_str}. "
            f"Estimated commitment: {round(accumulated_hours, 1)} hours."
        )

        milestone = RoadmapMilestone(
            id=str(uuid.uuid4()),
            roadmap_id=roadmap_id,
            title=milestone_title,
            description=milestone_desc,
            sequence_order=w,
            week_number=w,
            status="in_progress" if w == 1 else "pending",
        )
        db.add(milestone)

        weekly_schedule.append({
            "week_number": w,
            "title": milestone_title,
            "skills": distinct_skills,
            "topics": [t["topic_name"] for t in week_topics],
            "estimated_hours": round(accumulated_hours, 1),
            "milestone_id": milestone.id,
        })

    roadmap.weekly_schedule = weekly_schedule

    db.commit()
    db.refresh(roadmap)
    return roadmap


def get_learning_roadmaps(
    db: Session,
    career_profile_id: str,
) -> List[LearningRoadmap]:
    """Retrieve all historical learning roadmaps for a user, ordered newest first."""
    stmt = (
        select(LearningRoadmap)
        .where(LearningRoadmap.career_profile_id == career_profile_id)
        .order_by(LearningRoadmap.created_at.desc())
    )
    return list(db.execute(stmt).scalars().all())


def get_learning_roadmap(
    db: Session,
    career_profile_id: str,
    roadmap_id: str,
) -> Optional[LearningRoadmap]:
    """Retrieve full details of a specific learning roadmap."""
    stmt = select(LearningRoadmap).where(
        (LearningRoadmap.id == roadmap_id)
        & (LearningRoadmap.career_profile_id == career_profile_id)
    )
    return db.execute(stmt).scalar_one_or_none()


def delete_learning_roadmap(
    db: Session,
    career_profile_id: str,
    roadmap_id: str,
) -> bool:
    """Permanently delete a learning roadmap."""
    roadmap = get_learning_roadmap(db, career_profile_id, roadmap_id)
    if not roadmap:
        return False

    db.delete(roadmap)
    db.commit()
    return True


def update_topic_status(
    db: Session,
    career_profile_id: str,
    roadmap_id: str,
    topic_id: str,
    new_status: str,
) -> RoadmapTopic:
    """
    Update topic completion status ('not_started', 'in_progress', 'completed'),
    recalculate parent skill status, and update overall roadmap progress.
    """
    roadmap = get_learning_roadmap(db, career_profile_id, roadmap_id)
    if not roadmap:
        raise RoadmapNotFoundError(f"Roadmap '{roadmap_id}' not found.")

    stmt = select(RoadmapTopic).join(RoadmapSkill).where(
        (RoadmapTopic.id == topic_id)
        & (RoadmapSkill.roadmap_id == roadmap_id)
    )
    topic = db.execute(stmt).scalar_one_or_none()
    if not topic:
        raise RoadmapItemNotFoundError(f"Topic '{topic_id}' not found in roadmap '{roadmap_id}'.")

    topic.status = new_status
    if new_status == "completed":
        topic.completed_at = datetime.now(timezone.utc)
    else:
        topic.completed_at = None

    # Recalculate parent skill status
    parent_skill = topic.roadmap_skill
    all_topics = parent_skill.topics
    if all(t.status == "completed" for t in all_topics):
        parent_skill.status = "completed"
    elif any(t.status in ("in_progress", "completed") for t in all_topics):
        parent_skill.status = "in_progress"
    else:
        parent_skill.status = "not_started"

    # Recalculate roadmap completion metrics
    _recalculate_roadmap_progress(db, roadmap)

    db.commit()
    db.refresh(topic)
    return topic


def update_skill_status(
    db: Session,
    career_profile_id: str,
    roadmap_id: str,
    skill_id: str,
    new_status: str,
) -> RoadmapSkill:
    """
    Update skill status. When marked 'completed', automatically marks all
    child topics as completed.
    """
    roadmap = get_learning_roadmap(db, career_profile_id, roadmap_id)
    if not roadmap:
        raise RoadmapNotFoundError(f"Roadmap '{roadmap_id}' not found.")

    stmt = select(RoadmapSkill).where(
        (RoadmapSkill.id == skill_id)
        & (RoadmapSkill.roadmap_id == roadmap_id)
    )
    skill = db.execute(stmt).scalar_one_or_none()
    if not skill:
        raise RoadmapItemNotFoundError(f"Skill '{skill_id}' not found in roadmap '{roadmap_id}'.")

    skill.status = new_status

    if new_status == "completed":
        now = datetime.now(timezone.utc)
        for t in skill.topics:
            t.status = "completed"
            t.completed_at = now
    elif new_status == "not_started":
        for t in skill.topics:
            t.status = "not_started"
            t.completed_at = None

    _recalculate_roadmap_progress(db, roadmap)

    db.commit()
    db.refresh(skill)
    return skill


def update_milestone_status(
    db: Session,
    career_profile_id: str,
    roadmap_id: str,
    milestone_id: str,
    new_status: str,
) -> RoadmapMilestone:
    """Update milestone progress status ('pending', 'in_progress', 'completed')."""
    roadmap = get_learning_roadmap(db, career_profile_id, roadmap_id)
    if not roadmap:
        raise RoadmapNotFoundError(f"Roadmap '{roadmap_id}' not found.")

    stmt = select(RoadmapMilestone).where(
        (RoadmapMilestone.id == milestone_id)
        & (RoadmapMilestone.roadmap_id == roadmap_id)
    )
    milestone = db.execute(stmt).scalar_one_or_none()
    if not milestone:
        raise RoadmapItemNotFoundError(f"Milestone '{milestone_id}' not found in roadmap '{roadmap_id}'.")

    milestone.status = new_status
    if new_status == "completed":
        milestone.completed_at = datetime.now(timezone.utc)
    else:
        milestone.completed_at = None

    db.commit()
    db.refresh(milestone)
    return milestone


def get_roadmap_progress(
    db: Session,
    career_profile_id: str,
    roadmap_id: str,
) -> Dict[str, Any]:
    """Compute and retrieve comprehensive telemetry on roadmap progress."""
    roadmap = get_learning_roadmap(db, career_profile_id, roadmap_id)
    if not roadmap:
        raise RoadmapNotFoundError(f"Roadmap '{roadmap_id}' not found.")

    total_skills = len(roadmap.skills)
    completed_skills = sum(1 for s in roadmap.skills if s.status == "completed")

    total_topics = roadmap.total_topics_count
    completed_topics = roadmap.completed_topics_count

    # Calculate remaining hours
    remaining_hours = 0.0
    next_topic: Optional[Dict[str, Any]] = None

    for skill in sorted(roadmap.skills, key=lambda s: s.sequence_order):
        for topic in sorted(skill.topics, key=lambda t: t.sequence_order):
            if topic.status != "completed":
                remaining_hours += topic.estimated_hours
                if next_topic is None:
                    next_topic = {
                        "topic_id": topic.id,
                        "topic_name": topic.topic_name,
                        "skill_name": skill.skill_name,
                        "priority": skill.priority,
                        "estimated_hours": topic.estimated_hours,
                    }

    # Estimate current week based on completed topics
    topics_per_week = max(1, math.ceil(total_topics / max(1, roadmap.total_weeks)))
    current_week = min(roadmap.total_weeks, (completed_topics // topics_per_week) + 1)

    return {
        "roadmap_id": roadmap.id,
        "total_skills": total_skills,
        "completed_skills": completed_skills,
        "total_topics": total_topics,
        "completed_topics": completed_topics,
        "progress_percentage": roadmap.progress_percentage,
        "estimated_hours_remaining": round(remaining_hours, 1),
        "current_week": current_week,
        "status": roadmap.status,
        "next_recommended_topic": next_topic,
    }


def _recalculate_roadmap_progress(db: Session, roadmap: LearningRoadmap) -> None:
    """Internal helper to aggregate topic completions and update overall roadmap progress percentage."""
    all_topics = []
    for skill in roadmap.skills:
        all_topics.extend(skill.topics)

    total_count = len(all_topics)
    completed_count = sum(1 for t in all_topics if t.status == "completed")

    roadmap.total_topics_count = total_count
    roadmap.completed_topics_count = completed_count
    if total_count > 0:
        roadmap.progress_percentage = round((completed_count / total_count) * 100, 1)
    else:
        roadmap.progress_percentage = 0.0

    if completed_count == total_count and total_count > 0:
        roadmap.status = "completed"
    else:
        roadmap.status = "in_progress"

    roadmap.updated_at = datetime.now(timezone.utc)

