"""
Pydantic schemas for candidate learning objectives and interview prep preferences.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class LearningPreferenceBase(BaseModel):
    learning_objective: str | None = Field(default=None, description="Current primary skill or concept to learn")
    daily_learning_hours: float | None = Field(default=None, ge=0.0, le=24.0, description="Available study hours per day")
    preferred_language: str | None = Field(default=None, max_length=50, description="Preferred language for courses/docs")
    interview_preparation_type: str | None = Field(default=None, max_length=50, description="System Design, Coding, Behavioral")
    preferred_learning_style: str | None = Field(default=None, max_length=50, description="Hands-on projects, Videos, Docs")


class LearningPreferenceCreate(LearningPreferenceBase):
    pass


class LearningPreferenceUpdate(BaseModel):
    learning_objective: str | None = None
    daily_learning_hours: float | None = None
    preferred_language: str | None = None
    interview_preparation_type: str | None = None
    preferred_learning_style: str | None = None


class LearningPreferenceResponse(LearningPreferenceBase):
    id: str
    career_profile_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

