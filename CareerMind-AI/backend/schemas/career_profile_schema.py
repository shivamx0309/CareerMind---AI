"""
Pydantic schemas for user career profile management and onboarding.
"""

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


# Permitted categorical choices
CareerStatus = Literal["Student", "Fresher", "Experienced"]
JobType = Literal["Full-time", "Internship", "Contract", "Part-time"]
WorkMode = Literal["Remote", "Hybrid", "On-site"]


class CareerProfileBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=200, description="Full name of user")
    career_status: CareerStatus = Field(..., description="Student, Fresher, or Experienced")
    highest_education: str = Field(..., min_length=2, max_length=100, description="Highest degree or qualification level")
    degree: str = Field(..., min_length=2, max_length=150, description="Degree or qualification specialization")
    institution: str = Field(..., min_length=2, max_length=200, description="College, university, or institution")
    graduation_year: int = Field(..., ge=1970, le=2040, description="Year of graduation (1970-2040)")
    primary_target_role: str = Field(..., min_length=2, max_length=150, description="Primary job designation sought")
    preferred_job_type: JobType = Field(default="Full-time", description="Full-time, Internship, Contract, or Part-time")
    preferred_work_mode: WorkMode = Field(default="Remote", description="Remote, Hybrid, or On-site")
    preferred_locations: list[str] = Field(default_factory=list, description="Target locations or cities")
    career_objective: str | None = Field(default=None, max_length=2000, description="Basic career objective statement")

    @field_validator("full_name", "highest_education", "degree", "institution", "primary_target_role")
    @classmethod
    def validate_non_empty_strings(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Field cannot be empty or only whitespace")
        return trimmed

    @field_validator("preferred_locations")
    @classmethod
    def validate_locations(cls, v: list[str]) -> list[str]:
        cleaned = [loc.strip() for loc in v if isinstance(loc, str) and loc.strip()]
        if not cleaned:
            # Default to Remote/Anywhere if none specified
            return ["Anywhere"]
        return cleaned

    @field_validator("career_objective")
    @classmethod
    def clean_objective(cls, v: str | None) -> str | None:
        if v is None:
            return None
        trimmed = v.strip()
        return trimmed if trimmed else None


class CareerProfileCreate(CareerProfileBase):
    """Schema for registering a new career profile during onboarding."""
    pass


class CareerProfileUpdate(BaseModel):
    """Schema for updating an existing career profile."""
    full_name: str | None = Field(default=None, min_length=2, max_length=200)
    career_status: CareerStatus | None = None
    highest_education: str | None = Field(default=None, min_length=2, max_length=100)
    degree: str | None = Field(default=None, min_length=2, max_length=150)
    institution: str | None = Field(default=None, min_length=2, max_length=200)
    graduation_year: int | None = Field(default=None, ge=1970, le=2040)
    primary_target_role: str | None = Field(default=None, min_length=2, max_length=150)
    preferred_job_type: JobType | None = None
    preferred_work_mode: WorkMode | None = None
    preferred_locations: list[str] | None = None
    career_objective: str | None = Field(default=None, max_length=2000)

    @field_validator("full_name", "highest_education", "degree", "institution", "primary_target_role")
    @classmethod
    def validate_non_empty_strings(cls, v: str | None) -> str | None:
        if v is None:
            return None
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Field cannot be empty or only whitespace")
        return trimmed

    @field_validator("preferred_locations")
    @classmethod
    def validate_locations(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return None
        cleaned = [loc.strip() for loc in v if isinstance(loc, str) and loc.strip()]
        return cleaned if cleaned else ["Anywhere"]


class CareerProfileResponse(CareerProfileBase):
    """API response schema for a career profile."""
    id: str
    user_id: str
    onboarding_completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OnboardingStatusResponse(BaseModel):
    """API response schema checking whether local user has completed onboarding."""
    onboarding_completed: bool
    has_profile: bool
    full_name: str | None = None
    primary_target_role: str | None = None
    career_status: str | None = None
