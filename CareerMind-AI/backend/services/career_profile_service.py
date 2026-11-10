"""
Career profile service for single-user local MVP profile management and onboarding.
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from database.models.career_profile import CareerProfile
from database.models.career_goal import CareerGoal
from database.models.learning_preference import LearningPreference
from schemas.career_profile_schema import (
    CareerProfileCreate,
    CareerProfileUpdate,
    OnboardingStatusResponse,
)
from schemas.career_goal_schema import CareerGoalCreate, CareerGoalUpdate
from schemas.learning_preference_schema import LearningPreferenceCreate, LearningPreferenceUpdate

LOCAL_USER_ID = "local_user"


class ProfileAlreadyExistsError(Exception):
    """Raised when attempting to create a profile when one already exists for the local user."""
    pass


def get_local_career_profile(db: Session) -> Optional[CareerProfile]:
    """Retrieve the single local career profile if one exists."""
    stmt = select(CareerProfile).where(CareerProfile.user_id == LOCAL_USER_ID)
    return db.execute(stmt).scalar_one_or_none()


def get_or_create_local_career_profile(db: Session) -> CareerProfile:
    """
    Retrieve the local career profile, or create a minimal un-onboarded profile
    if none exists yet, ensuring resume uploads and records always have a valid owner.
    """
    profile = get_local_career_profile(db)
    if not profile:
        profile = CareerProfile(
            user_id=LOCAL_USER_ID,
            full_name="Local User",
            career_status="Fresher",
            highest_education="Bachelor's",
            degree="General",
            institution="University",
            graduation_year=2026,
            primary_target_role="Software Engineer",
            preferred_job_type="Full-time",
            preferred_work_mode="Remote",
            preferred_locations=[],
            career_objective=None,
            onboarding_completed=False,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def get_onboarding_status(db: Session) -> OnboardingStatusResponse:
    """Check whether the local user has completed onboarding."""
    profile = get_local_career_profile(db)
    if not profile:
        return OnboardingStatusResponse(
            onboarding_completed=False,
            has_profile=False,
            full_name=None,
            primary_target_role=None,
            career_status=None,
        )

    return OnboardingStatusResponse(
        onboarding_completed=bool(profile.onboarding_completed),
        has_profile=True,
        full_name=profile.full_name,
        primary_target_role=profile.primary_target_role,
        career_status=profile.career_status,
    )


def create_local_career_profile(
    db: Session,
    profile_in: CareerProfileCreate,
) -> CareerProfile:
    """
    Create a new local career profile.
    Raises ProfileAlreadyExistsError if a local profile is already registered.
    """
    existing = get_local_career_profile(db)
    if existing:
        raise ProfileAlreadyExistsError("A career profile already exists for the local user.")

    new_profile = CareerProfile(
        user_id=LOCAL_USER_ID,
        **profile_in.model_dump(),
        onboarding_completed=True,
    )
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile


def update_local_career_profile(
    db: Session,
    profile_in: CareerProfileUpdate,
) -> Optional[CareerProfile]:
    """
    Update fields on the existing local career profile.
    Returns None if no profile exists.
    """
    profile = get_local_career_profile(db)
    if not profile:
        return None

    update_data = profile_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    # Ensure onboarding_completed remains True when updated
    profile.onboarding_completed = True

    db.commit()
    db.refresh(profile)
    return profile


def create_or_update_local_career_profile(
    db: Session,
    profile_in: CareerProfileCreate,
) -> CareerProfile:
    """
    Upsert helper for testing or legacy workflows.
    """
    existing = get_local_career_profile(db)
    if existing:
        for field, value in profile_in.model_dump().items():
            setattr(existing, field, value)
        existing.onboarding_completed = True
        db.commit()
        db.refresh(existing)
        return existing

    new_profile = CareerProfile(
        user_id=LOCAL_USER_ID,
        **profile_in.model_dump(),
        onboarding_completed=True,
    )
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile


def set_career_goals(
    db: Session,
    career_profile_id: str,
    goals_in: CareerGoalCreate,
) -> CareerGoal:
    """Set or replace career goals for a career profile."""
    stmt = select(CareerGoal).where(CareerGoal.career_profile_id == career_profile_id)
    existing = db.execute(stmt).scalar_one_or_none()

    if existing:
        for field, value in goals_in.model_dump().items():
            setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return existing

    new_goals = CareerGoal(
        career_profile_id=career_profile_id,
        **goals_in.model_dump(),
    )
    db.add(new_goals)
    db.commit()
    db.refresh(new_goals)
    return new_goals


def set_learning_preferences(
    db: Session,
    career_profile_id: str,
    prefs_in: LearningPreferenceCreate,
) -> LearningPreference:
    """Set or replace learning preferences for a career profile."""
    stmt = select(LearningPreference).where(LearningPreference.career_profile_id == career_profile_id)
    existing = db.execute(stmt).scalar_one_or_none()

    if existing:
        for field, value in prefs_in.model_dump().items():
            setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return existing

    new_prefs = LearningPreference(
        career_profile_id=career_profile_id,
        **prefs_in.model_dump(),
    )
    db.add(new_prefs)
    db.commit()
    db.refresh(new_prefs)
    return new_prefs
