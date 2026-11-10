"""
Learning Roadmap API Endpoints.
Provides personalized curriculum generation from SkillGapReports, structured weekly milestone
tracking, verified learning resources, progress telemetry, and candidate study preferences.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from database.session import get_db
from database.models.learning_preference import LearningPreference
from schemas.learning_preference_schema import (
    LearningPreferenceCreate,
    LearningPreferenceResponse,
)
from schemas.roadmap_schema import (
    RoadmapGenerateRequest,
    LearningRoadmapResponse,
    LearningRoadmapSummaryResponse,
    RoadmapTopicResponse,
    RoadmapSkillResponse,
    RoadmapMilestoneResponse,
    RoadmapProgressResponse,
    TopicStatusUpdateRequest,
    SkillStatusUpdateRequest,
    MilestoneStatusUpdateRequest,
)
from services import (
    career_profile_service,
    roadmap_service,
)
from services.roadmap_service import (
    SkillGapReportNotFoundError,
    InvalidReportStateError,
    RoadmapNotFoundError,
    RoadmapItemNotFoundError,
    RoadmapServiceError,
)

router = APIRouter(
    prefix="/learning",
    tags=["Learning Roadmap"],
)


@router.get(
    "/preferences",
    response_model=LearningPreferenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get candidate learning preferences",
    description="Retrieve study preferences (daily study hours, learning style, interview target). Initializes defaults if not yet set.",
)
def get_learning_preferences(
    db: Session = Depends(get_db),
):
    """Retrieve candidate learning preferences, automatically bootstrapping defaults if needed."""
    profile = career_profile_service.get_or_create_local_career_profile(db)
    stmt = select(LearningPreference).where(LearningPreference.career_profile_id == profile.id)
    prefs = db.execute(stmt).scalar_one_or_none()

    if not prefs:
        prefs = career_profile_service.set_learning_preferences(
            db,
            profile.id,
            LearningPreferenceCreate(
                learning_objective=profile.primary_target_role or "Software Engineer",
                daily_learning_hours=2.0,
                preferred_language="English",
                interview_preparation_type="Coding & Architecture",
                preferred_learning_style="Hands-on projects & Documentation",
            ),
        )
    return prefs


@router.put(
    "/preferences",
    response_model=LearningPreferenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Update candidate learning preferences",
    description="Update candidate daily learning hours, target role objectives, and preferred learning styles.",
)
def update_learning_preferences(
    prefs_in: LearningPreferenceCreate,
    db: Session = Depends(get_db),
):
    """Update or upsert learning preferences for the local profile."""
    profile = career_profile_service.get_or_create_local_career_profile(db)
    return career_profile_service.set_learning_preferences(db, profile.id, prefs_in)


@router.post(
    "/roadmaps/generate",
    response_model=LearningRoadmapResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate personalized learning roadmap from skill gap report",
    description="Convert a saved SkillGapReport into a dependency-ordered, weekly structured learning plan.",
)
def generate_roadmap(
    request: RoadmapGenerateRequest,
    db: Session = Depends(get_db),
):
    """Generate and persist a personalized learning roadmap."""
    profile = career_profile_service.get_or_create_local_career_profile(db)
    try:
        roadmap = roadmap_service.generate_learning_roadmap(
            db=db,
            career_profile_id=profile.id,
            skill_gap_report_id=request.skill_gap_report_id,
            weekly_study_hours=request.weekly_study_hours,
            custom_title=request.title,
        )
        return roadmap
    except SkillGapReportNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except InvalidReportStateError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except RoadmapServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/roadmaps",
    response_model=List[LearningRoadmapSummaryResponse],
    status_code=status.HTTP_200_OK,
    summary="List generated learning roadmaps",
    description="Retrieve all historical learning roadmaps for the authenticated candidate, ordered newest first.",
)
def list_roadmaps(
    db: Session = Depends(get_db),
):
    """List historical roadmaps for the active profile."""
    profile = career_profile_service.get_or_create_local_career_profile(db)
    return roadmap_service.get_learning_roadmaps(db, profile.id)


@router.get(
    "/roadmaps/{roadmap_id}",
    response_model=LearningRoadmapResponse,
    status_code=status.HTTP_200_OK,
    summary="Get full learning roadmap details",
    description="Retrieve full learning roadmap details including skills, syllabus topics, verified resources, and weekly milestones.",
)
def get_roadmap(
    roadmap_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve full details for a single roadmap."""
    profile = career_profile_service.get_or_create_local_career_profile(db)
    roadmap = roadmap_service.get_learning_roadmap(db, profile.id, roadmap_id)
    if not roadmap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Learning roadmap '{roadmap_id}' was not found.",
        )
    return roadmap


@router.patch(
    "/roadmaps/{roadmap_id}/topics/{topic_id}",
    response_model=RoadmapTopicResponse,
    status_code=status.HTTP_200_OK,
    summary="Update topic progress status",
    description="Update topic completion ('not_started', 'in_progress', 'completed') and recalculate parent skill and roadmap progress.",
)
def update_topic_status(
    roadmap_id: str,
    topic_id: str,
    body: TopicStatusUpdateRequest,
    db: Session = Depends(get_db),
):
    """Update completion status of an individual topic."""
    profile = career_profile_service.get_or_create_local_career_profile(db)
    try:
        topic = roadmap_service.update_topic_status(
            db=db,
            career_profile_id=profile.id,
            roadmap_id=roadmap_id,
            topic_id=topic_id,
            new_status=body.status,
        )
        return topic
    except (RoadmapNotFoundError, RoadmapItemNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/roadmaps/{roadmap_id}/skills/{skill_id}",
    response_model=RoadmapSkillResponse,
    status_code=status.HTTP_200_OK,
    summary="Update skill module status",
    description="Update skill module status. Marking 'completed' automatically marks all child topics completed.",
)
def update_skill_status(
    roadmap_id: str,
    skill_id: str,
    body: SkillStatusUpdateRequest,
    db: Session = Depends(get_db),
):
    """Update status of a skill module."""
    profile = career_profile_service.get_or_create_local_career_profile(db)
    try:
        skill = roadmap_service.update_skill_status(
            db=db,
            career_profile_id=profile.id,
            roadmap_id=roadmap_id,
            skill_id=skill_id,
            new_status=body.status,
        )
        return skill
    except (RoadmapNotFoundError, RoadmapItemNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/roadmaps/{roadmap_id}/milestones/{milestone_id}",
    response_model=RoadmapMilestoneResponse,
    status_code=status.HTTP_200_OK,
    summary="Update milestone status",
    description="Update weekly milestone completion status ('pending', 'in_progress', 'completed').",
)
def update_milestone_status(
    roadmap_id: str,
    milestone_id: str,
    body: MilestoneStatusUpdateRequest,
    db: Session = Depends(get_db),
):
    """Update status of a weekly milestone."""
    profile = career_profile_service.get_or_create_local_career_profile(db)
    try:
        milestone = roadmap_service.update_milestone_status(
            db=db,
            career_profile_id=profile.id,
            roadmap_id=roadmap_id,
            milestone_id=milestone_id,
            new_status=body.status,
        )
        return milestone
    except (RoadmapNotFoundError, RoadmapItemNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/roadmaps/{roadmap_id}/progress",
    response_model=RoadmapProgressResponse,
    status_code=status.HTTP_200_OK,
    summary="Get roadmap progress telemetry",
    description="Compute comprehensive progress metrics including completion percentage, remaining hours, and next recommended study topic.",
)
def get_roadmap_progress(
    roadmap_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve detailed progress telemetry for a roadmap."""
    profile = career_profile_service.get_or_create_local_career_profile(db)
    try:
        return roadmap_service.get_roadmap_progress(
            db=db,
            career_profile_id=profile.id,
            roadmap_id=roadmap_id,
        )
    except RoadmapNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.delete(
    "/roadmaps/{roadmap_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a learning roadmap",
    description="Permanently delete a learning roadmap and cascade all associated skills, topics, resources, and milestones.",
)
def delete_roadmap(
    roadmap_id: str,
    db: Session = Depends(get_db),
):
    """Delete a learning roadmap by ID."""
    profile = career_profile_service.get_or_create_local_career_profile(db)
    deleted = roadmap_service.delete_learning_roadmap(
        db=db,
        career_profile_id=profile.id,
        roadmap_id=roadmap_id,
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Learning roadmap '{roadmap_id}' was not found.",
        )
    return None

