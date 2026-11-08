"""
Pydantic schemas for candidate career goals and compensation expectations.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class CareerGoalBase(BaseModel):
    target_roles: list[str] = Field(default_factory=list, description="Target job titles")
    preferred_locations: list[str] = Field(default_factory=list, description="Target cities or regions")
    preferred_work_modes: list[str] = Field(default_factory=list, description="Remote, Hybrid, On-site")
    preferred_job_types: list[str] = Field(default_factory=list, description="Full-time, Internship, etc.")
    expected_salary: str | None = Field(default=None, max_length=100, description="Optional target compensation")
    job_search_timeline: str | None = Field(default=None, max_length=50, description="Immediately, 1-3 months, Exploring")


class CareerGoalCreate(CareerGoalBase):
    pass


class CareerGoalUpdate(BaseModel):
    target_roles: list[str] | None = None
    preferred_locations: list[str] | None = None
    preferred_work_modes: list[str] | None = None
    preferred_job_types: list[str] | None = None
    expected_salary: str | None = None
    job_search_timeline: str | None = None


class CareerGoalResponse(CareerGoalBase):
    id: str
    career_profile_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

