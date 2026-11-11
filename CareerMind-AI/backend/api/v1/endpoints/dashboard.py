"""
API endpoints for Dashboard Career Insights (Phase 6).

Exposes:
- GET /api/v1/dashboard/insights: Centralized, explainable candidate telemetry.
"""

import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.session import get_db
from schemas.dashboard_schema import DashboardInsightsResponse
from services.dashboard_service import get_dashboard_insights

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/dashboard/insights",
    response_model=DashboardInsightsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get aggregated real candidate career insights for dashboard",
    description=(
        "Retrieves real, non-fabricated career intelligence metrics including "
        "parsed resume skills, job matching status, skill gap benchmarks, "
        "authoritative roadmap progress, and mock interview performance history."
    ),
)
async def get_dashboard_insights_endpoint(
    db: Session = Depends(get_db),
) -> DashboardInsightsResponse:
    """Retrieve centralized real candidate career insights."""
    return get_dashboard_insights(db, user_id="local_user")

