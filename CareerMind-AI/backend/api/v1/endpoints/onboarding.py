"""
API endpoints for user career profile onboarding and profile management (Phase C & D).
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.session import get_db
from schemas.career_profile_schema import (
    CareerProfileCreate,
    CareerProfileUpdate,
    CareerProfileResponse,
    OnboardingStatusResponse,
)
from services.career_profile_service import (
    get_local_career_profile,
    create_local_career_profile,
    update_local_career_profile,
    get_onboarding_status,
    ProfileAlreadyExistsError,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/onboarding",
    tags=["Onboarding & Profile"],
)


@router.get(
    "/status",
    response_model=OnboardingStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Check local onboarding completion status",
)
def check_onboarding_status(
    db: Session = Depends(get_db),
):
    """
    Check whether the single local user has registered their career profile.
    Returns onboarding_completed=True/False without throwing 404.
    """
    return get_onboarding_status(db)


@router.get(
    "/profile",
    response_model=CareerProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve the registered career profile",
)
def get_career_profile(
    db: Session = Depends(get_db),
):
    """
    Retrieve the single local user's registered career profile.
    Throws 404 if onboarding has not been completed.
    """
    profile = get_local_career_profile(db)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career profile not found. Please complete onboarding first.",
        )
    return profile


@router.post(
    "/profile",
    response_model=CareerProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register career profile during onboarding",
)
def register_career_profile(
    profile_in: CareerProfileCreate,
    db: Session = Depends(get_db),
):
    """
    Register the single local user's career profile during onboarding.
    Enforces the single-user local boundary.
    Returns HTTP 409 Conflict if a profile already exists.
    """
    try:
        created = create_local_career_profile(db, profile_in)
        return created
    except ProfileAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )
    except Exception as exc:
        logger.exception("Unexpected error while registering career profile: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register career profile due to an internal server error.",
        )


@router.put(
    "/profile",
    response_model=CareerProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Update registered career profile",
)
def update_career_profile(
    profile_in: CareerProfileUpdate,
    db: Session = Depends(get_db),
):
    """
    Update the single local user's existing career profile.
    Returns HTTP 404 if no profile exists yet.
    """
    try:
        updated = update_local_career_profile(db, profile_in)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Career profile not found. Please complete onboarding first.",
            )
        return updated
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected error while updating career profile: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update career profile due to an internal server error.",
        )

