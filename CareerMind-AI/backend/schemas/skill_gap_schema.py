"""
Pydantic schemas for the Skill Gap Analysis Engine (Phase 2).
Defines structured request models, item classifications, category breakdowns,
and persistent report contracts.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SkillGapAnalysisRequest(BaseModel):
    """Request payload to initiate a Skill Gap Analysis."""

    target_role: str = Field(..., description="Role benchmark identifier (e.g. 'sde', 'backend_developer')")
    resume_id: Optional[str] = Field(
        default=None,
        description="Optional ResumeRecord UUID or 32-character hexadecimal file_id. If omitted, the default resume is used.",
    )


class SkillGapItem(BaseModel):
    """Detailed evaluation of an individual benchmark skill against candidate evidence."""

    skill_name: str = Field(description="Canonical benchmark skill name")
    category: str = Field(description="Technical category (e.g. 'programming_languages', 'databases')")
    importance: str = Field(description="'required' or 'preferred'")
    status: str = Field(description="'exact_match', 'alias_match', 'semantically_related', or 'missing'")
    match_confidence: float = Field(description="Match weight: 1.0 (exact/alias), 0.6 (related), 0.0 (missing)")
    weight: float = Field(default=1.0, description="Importance weight applied in scoring")
    matched_skill: Optional[str] = Field(default=None, description="Actual token or skill name found in candidate profile")
    evidence_source: Optional[str] = Field(default=None, description="Section where evidence was detected")
    evidence_context: Optional[str] = Field(default=None, description="Contextual snippet where skill was evidenced")

    model_config = ConfigDict(from_attributes=True)


class CategoryGapBreakdown(BaseModel):
    """Aggregate competency metrics for a technical skill category."""

    category: str
    total_skills: int
    matched_count: int
    related_count: int
    missing_count: int
    coverage_percentage: float

    model_config = ConfigDict(from_attributes=True)


class SkillGapReportResponse(BaseModel):
    """Full detailed Skill Gap Analysis report."""

    id: str
    career_profile_id: str
    resume_record_id: str
    resume_name: Optional[str] = None
    target_role: str
    role_title: str
    benchmark_version: str
    overall_score: Optional[float] = None
    required_coverage_percentage: Optional[float] = None
    preferred_coverage_percentage: Optional[float] = None

    total_required_skills: int
    matched_required_skills_count: int
    related_required_skills_count: int
    missing_required_skills_count: int

    total_preferred_skills: int
    matched_preferred_skills_count: int
    related_preferred_skills_count: int
    missing_preferred_skills_count: int

    matched_skills: List[SkillGapItem] = Field(default_factory=list)
    related_skills: List[SkillGapItem] = Field(default_factory=list)
    missing_required_skills: List[str] = Field(default_factory=list)
    missing_preferred_skills: List[str] = Field(default_factory=list)
    category_breakdown: List[CategoryGapBreakdown] = Field(default_factory=list)

    analysis_status: str = Field(default="completed", description="'completed', 'insufficient_benchmark', or 'no_candidate_skills'")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SkillGapReportSummaryResponse(BaseModel):
    """Lightweight summary of a historical Skill Gap Analysis report."""

    id: str
    career_profile_id: str
    resume_record_id: str
    target_role: str
    role_title: str
    overall_score: Optional[float] = None
    required_coverage_percentage: Optional[float] = None
    analysis_status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoleBenchmarkSummaryResponse(BaseModel):
    """Public summary of a supported career role benchmark."""

    role_id: str
    title: str
    description: str
    domain: str
    version: str
    required_skills_count: int
    preferred_skills_count: int
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

