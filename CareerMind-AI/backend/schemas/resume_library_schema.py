"""
Pydantic schemas for resume library records and parsed details.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from schemas.candidate_schema import CandidateProfile


class ResumeRecordResponse(BaseModel):
    id: str
    career_profile_id: str
    file_id: str
    display_name: str
    original_filename: str
    file_path: str
    file_size: int
    is_default: bool
    upload_status: str
    extraction_status: str
    parsing_status: str
    created_at: datetime
    updated_at: datetime
    last_parsed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ResumeRecordRename(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=200, description="New user-facing label for resume")


class ResumeSkillResponse(BaseModel):
    id: str
    skill_name: str
    category: str
    confidence: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeEducationResponse(BaseModel):
    id: str
    degree: str | None = None
    institution: str | None = None
    specialization: str | None = None
    start_year: str | None = None
    end_year: str | None = None
    grade_or_cgpa: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeExperienceResponse(BaseModel):
    id: str
    job_title: str | None = None
    company: str | None = None
    employment_type: str | None = None
    location: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeProjectResponse(BaseModel):
    id: str
    project_name: str | None = None
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)
    project_url: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeCertificationResponse(BaseModel):
    id: str
    certification_name: str | None = None
    issuing_organization: str | None = None
    issue_date: str | None = None
    credential_url: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeProfileDetailResponse(BaseModel):
    id: str
    resume_record_id: str
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    linkedin: str | None = None
    github: str | None = None
    portfolio: str | None = None
    location: str | None = None
    professional_summary: str | None = None
    achievements: list[dict] = Field(default_factory=list)
    skills: list[ResumeSkillResponse] = Field(default_factory=list)
    educations: list[ResumeEducationResponse] = Field(default_factory=list)
    experiences: list[ResumeExperienceResponse] = Field(default_factory=list)
    projects: list[ResumeProjectResponse] = Field(default_factory=list)
    certifications: list[ResumeCertificationResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeDetailResponse(ResumeRecordResponse):
    candidate: CandidateProfile | None = None
    profile_detail: ResumeProfileDetailResponse | None = None

    model_config = ConfigDict(from_attributes=True)
