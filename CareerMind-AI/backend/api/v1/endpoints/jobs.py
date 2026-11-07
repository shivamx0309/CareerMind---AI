"""
API Endpoints for Job Matching (Phase 5.6).

Exposes:
- POST /api/v1/jobs/match: Evaluates candidate resume against target job description.
"""

import logging
from fastapi import APIRouter, HTTPException, status

from api.v1.endpoints import resume as resume_endpoint
from schemas.matching_schema import (
    JobMatchRequest,
    JobMatchResponse,
)
from matching_engine.matching_service import execute_job_matching

logger = logging.getLogger(__name__)

router = APIRouter()

# Upload directory reference (inherits from resume endpoint to support testing/monkeypatching)
UPLOAD_DIR = resume_endpoint.UPLOAD_DIR


@router.post(
    "/jobs/match",
    response_model=JobMatchResponse,
    status_code=status.HTTP_200_OK,
    summary="Match an uploaded candidate resume against a job description",
    description=(
        "Orchestrates end-to-end multi-dimensional job matching including "
        "skills normalization, experience tenure evaluation, education credentials alignment, "
        "deterministic lexical similarity, explainable score breakdown, and prioritized recommendations."
    ),
)
async def match_job(request: JobMatchRequest) -> JobMatchResponse:
    """
    Match a validated, previously uploaded candidate resume with a target Job Description.

    - Validates file_id format (32-character hexadecimal UUID).
    - Checks that the resume file exists in the storage directory.
    - Prevents directory traversal attacks.
    - Extracts text and candidate profile safely.
    - Computes explainable match scoring across all 5 dimensions.
    - Generates actionable, prioritized learning recommendations for identified gaps.
    """
    # 1. Enforce file_id presence
    if not request.file_id or not request.file_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File ID is missing or invalid.",
        )

    # 2. Execute matching pipeline via matching service
    try:
        response = execute_job_matching(
            file_id=request.file_id,
            job_description=request.job_description,
            job_title=request.job_title,
            company=request.company,
            location=request.location,
            upload_dir=UPLOAD_DIR,
        )
        return response

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file path.",
        ) from exc

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume file not found.",
        ) from exc

    except ValueError as exc:
        error_msg = str(exc)
        if "Invalid file ID format" in error_msg or "File ID is missing" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            ) from exc

        # PDF parsing, empty text, or unprocessable candidate profile
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error_msg,
        ) from exc

    except HTTPException:
        raise

    except Exception as exc:
        logger.error("Unexpected error in job matching for file_id %s: %s", request.file_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while matching the job description.",
        ) from exc
