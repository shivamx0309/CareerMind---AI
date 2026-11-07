"""
Pydantic schemas for the Job Matching Engine (Phase 5).

Defines:
- Input requests for job description submissions
- Parsed job description structures (skills, experience, education, responsibilities)
- Skill match classifications (exact match, alias match, semantically related, missing)
- Evidence-based component scoring with explicit availability tracking and weight normalization
- Consolidated job match response models
"""

from enum import Enum
from pydantic import BaseModel, Field, field_validator


class ComponentAvailability(str, Enum):
    """Component evaluation availability states."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    INSUFFICIENT_DATA = "insufficient_data"


class SkillRequirementType(str, Enum):
    """Requirement priority for skills in job descriptions."""

    REQUIRED = "required"
    PREFERRED = "preferred"


class SkillMatchStatus(str, Enum):
    """Classification of candidate skill match against JD requirements."""

    EXACT_MATCH = "exact_match"
    ALIAS_MATCH = "alias_match"
    SEMANTICALLY_RELATED = "semantically_related"
    MISSING = "missing"


class SkillMatchItem(BaseModel):
    """Detailed matching record for an individual JD skill."""

    skill: str = Field(description="Canonical skill name from JD")
    requirement_type: SkillRequirementType = Field(
        default=SkillRequirementType.REQUIRED,
        description="Whether skill was required or preferred in the JD",
    )
    status: SkillMatchStatus = Field(
        description="Match classification (exact_match, alias_match, semantically_related, missing)"
    )
    candidate_evidence: str | None = Field(
        default=None,
        description="Exact phrase or skill found in candidate profile",
    )
    evidence_source: str | None = Field(
        default=None,
        description="Candidate section where evidence was found (technical_skills, experience, projects, certifications)",
    )
    match_confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score for this match (1.0 for exact/alias)",
    )
    original_jd_phrase: str | None = Field(
        default=None,
        description="Original phrase or line from the job description",
    )


class ExperienceRequirement(BaseModel):
    """Structured experience expectations extracted from JD."""

    minimum_years: float | None = Field(
        default=None,
        description="Minimum required years of experience",
    )
    maximum_years: float | None = Field(
        default=None,
        description="Upper range of required years if specified (e.g. 3-5 years)",
    )
    level: str | None = Field(
        default=None,
        description="Seniority level (e.g. Entry-level, Mid-level, Senior, Lead)",
    )
    is_required: bool = Field(
        default=True,
        description="Whether experience duration is strictly required or preferred",
    )
    evidence: str | None = Field(
        default=None,
        description="Verbatim sentence from JD mentioning experience requirement",
    )


class EducationRequirement(BaseModel):
    """Structured educational expectations extracted from JD."""

    required_degree: str | None = Field(
        default=None,
        description="Degree level required (Bachelor, Master, PhD, Associate)",
    )
    fields_of_study: list[str] = Field(
        default_factory=list,
        description="Acceptable fields of study (e.g. Computer Science, Engineering)",
    )
    is_required: bool = Field(
        default=True,
        description="Whether degree is strictly required or preferred",
    )
    evidence: str | None = Field(
        default=None,
        description="Verbatim sentence from JD mentioning education requirement",
    )


class ExperienceAssessmentStatus(str, Enum):
    """Classification of candidate experience against JD expectations."""

    EXCEEDS_REQUIREMENT = "exceeds_requirement"
    MEETS_REQUIREMENT = "meets_requirement"
    PARTIAL = "partial"
    BELOW_REQUIREMENT = "below_requirement"
    NOT_REQUIRED = "not_required"
    INSUFFICIENT_DATA = "insufficient_data"


class ExperienceMatchResult(BaseModel):
    """Structured evaluation of candidate work, internship, and project experience."""

    required_years: float | None = Field(
        default=None,
        description="Minimum years of professional experience expected by JD",
    )
    required_level: str | None = Field(
        default=None,
        description="Seniority level expected by JD (e.g. Senior, Lead, Entry-level)",
    )
    is_required: bool = Field(
        default=True,
        description="Whether professional experience was strictly required",
    )
    professional_years: float | None = Field(
        default=None,
        description="Total verified professional employment years (excluding internships and projects, without overlap)",
    )
    internship_years: float | None = Field(
        default=None,
        description="Total verified internship duration years (without overlap)",
    )
    internship_entries: list[dict] = Field(
        default_factory=list,
        description="Identified internship roles and durations",
    )
    project_evidence: list[dict] = Field(
        default_factory=list,
        description="Relevant project portfolio evidence with tech stack alignment",
    )
    relevant_responsibilities: list[str] = Field(
        default_factory=list,
        description="Candidate responsibilities demonstrating skills relevant to the target role",
    )
    unrelated_responsibilities: list[str] = Field(
        default_factory=list,
        description="Candidate responsibilities outside the scope of the target role",
    )
    assessment: ExperienceAssessmentStatus = Field(
        description="Evaluation status: exceeds, meets, partial, below, not_required, or insufficient_data",
    )
    missing_information: list[str] = Field(
        default_factory=list,
        description="Information gaps such as missing employment dates or undefined durations",
    )
    evidence_sources: list[str] = Field(
        default_factory=list,
        description="Sources providing evidence for experience assessment (experience, projects)",
    )
    explanation: str = Field(
        description="Clear narrative explanation of the experience comparison",
    )


class EducationMatchStatus(str, Enum):
    """Classification of candidate education against JD expectations."""

    EXACT_MATCH = "exact_match"
    RELATED_MATCH = "related_match"
    MISSING = "missing"
    NOT_REQUIRED = "not_required"
    INSUFFICIENT_DATA = "insufficient_data"


class EducationMatchResult(BaseModel):
    """Structured evaluation of candidate educational credentials against JD expectations."""

    required_degree: str | None = Field(
        default=None,
        description="Degree level required or preferred by JD (Bachelor, Master, PhD, Associate)",
    )
    required_fields: list[str] = Field(
        default_factory=list,
        description="Fields of study or majors required/preferred by JD",
    )
    is_required: bool = Field(
        default=True,
        description="Whether degree was strictly required or preferred",
    )
    candidate_degree: str | None = Field(
        default=None,
        description="Highest or best-matching degree found on candidate profile",
    )
    candidate_field: str | None = Field(
        default=None,
        description="Candidate field of study / specialization",
    )
    candidate_institution: str | None = Field(
        default=None,
        description="Educational institution attended by candidate",
    )
    candidate_grade: str | None = Field(
        default=None,
        description="Reported academic grade or CGPA (never invented)",
    )
    status: EducationMatchStatus = Field(
        description="Classification: exact_match, related_match, missing, not_required, or insufficient_data",
    )
    degree_match: bool = Field(
        default=False,
        description="True if candidate degree meets or exceeds required degree level",
    )
    field_match: bool = Field(
        default=False,
        description="True if candidate field of study aligns with required disciplines",
    )
    evidence: str | None = Field(
        default=None,
        description="Verbatim education line or evidence from candidate profile",
    )
    explanation: str = Field(
        description="Clear narrative explanation of the education comparison",
    )


class ParsedJobDescription(BaseModel):
    """Structured representation of an analyzed job posting."""

    raw_text: str = Field(description="Original job description text submitted")
    job_title: str | None = Field(
        default=None,
        description="Target job title",
    )
    company: str | None = Field(
        default=None,
        description="Hiring company or organization",
    )
    location: str | None = Field(
        default=None,
        description="Job location or work mode (e.g. Remote, Hybrid, City)",
    )
    required_skills: list[str] = Field(
        default_factory=list,
        description="Mandatory skills extracted from requirements/must-have sections",
    )
    preferred_skills: list[str] = Field(
        default_factory=list,
        description="Nice-to-have or preferred skills extracted from JD",
    )
    skill_evidence: dict[str, str] = Field(
        default_factory=dict,
        description="Mapping from canonical skill name to exact context line in JD",
    )
    experience_requirement: ExperienceRequirement = Field(
        default_factory=ExperienceRequirement,
        description="Experience duration and seniority requirements",
    )
    education_requirement: EducationRequirement = Field(
        default_factory=EducationRequirement,
        description="Educational degree and discipline requirements",
    )
    responsibilities: list[str] = Field(
        default_factory=list,
        description="Core duties and responsibilities mentioned in the role",
    )
    keywords: list[str] = Field(
        default_factory=list,
        description="High-relevance domain keywords extracted from JD",
    )


class ComponentScore(BaseModel):
    """
    Transparent evaluation of a single scoring component.

    Explicitly models availability, raw score, base weight, and normalized weight
    to avoid unfair penalties or inflated scores for unassessed dimensions.
    """

    component_name: str = Field(description="Name of the component (e.g. required_skills)")
    availability: ComponentAvailability = Field(
        default=ComponentAvailability.AVAILABLE,
        description="Component availability state (available, unavailable, insufficient_data)",
    )
    raw_score: float | None = Field(
        default=None,
        ge=0.0,
        le=100.0,
        description="Score between 0.0 and 100.0 if component was assessed, else None",
    )
    base_weight: float = Field(
        ge=0.0,
        le=1.0,
        description="Default configured weight (summing to 1.0 across all components)",
    )
    normalized_weight: float = Field(
        ge=0.0,
        le=1.0,
        description="Effective weight after redistributing weights of unavailable components",
    )
    weighted_contribution: float = Field(
        ge=0.0,
        le=100.0,
        description="Contribution of this component to the overall score (raw_score * normalized_weight)",
    )
    evidence: list[str] = Field(
        default_factory=list,
        description="Human-readable supporting evidence points for this score",
    )
    reason: str | None = Field(
        default=None,
        description="Explanation when component is unavailable or why score was awarded",
    )


class MatchScoreBreakdown(BaseModel):
    """Comprehensive, explainable score breakdown."""

    overall_score: float | None = Field(
        default=None,
        ge=0.0,
        le=100.0,
        description="Aggregated match score between 0.0 and 100.0, or None if not assessable",
    )
    match_classification: str = Field(
        description="Classification: Strong Match (80-100), Moderate Match (60-79), Partial Match (40-59), Low Match (0-39), or Not assessable",
    )
    components: dict[str, ComponentScore] = Field(
        default_factory=dict,
        description="Detailed evaluation per dimension",
    )
    weight_normalization_applied: bool = Field(
        default=False,
        description="True if weights were re-normalized due to unavailable components",
    )
    explanation: str = Field(
        description="Clear narrative explanation of the score calculation",
    )


class RecommendationPriority(str, Enum):
    """Action priority level for recommendations."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecommendationCategory(str, Enum):
    """Domain category for actionable recommendations."""

    REQUIRED_SKILL = "required_skill"
    PREFERRED_SKILL = "preferred_skill"
    RELATED_SKILL = "related_skill"
    EXPERIENCE = "experience"
    PROJECT = "project"
    EDUCATION = "education"


class ActionableRecommendation(BaseModel):
    """
    Structured, evidence-grounded recommendation to bridge job-match gaps.

    Traceable directly to JD requirements, missing skills, experience duration,
    or education criteria.
    """

    recommendation_id: str = Field(
        description="Unique deterministic identifier for deduplication and client keys",
    )
    category: RecommendationCategory = Field(
        description="Category: required_skill, preferred_skill, related_skill, experience, project, education",
    )
    title: str = Field(
        description="Concise, action-oriented headline summarizing the recommendation",
    )
    description: str = Field(
        description="Detailed actionable guidance explaining the gap and how to bridge it",
    )
    priority: RecommendationPriority = Field(
        description="Priority ranking: high, medium, low",
    )
    related_requirement: str = Field(
        description="Specific JD skill or requirement this recommendation addresses",
    )
    reason: str = Field(
        description="Justification based on match findings and candidate profile",
    )
    candidate_evidence: str | None = Field(
        default=None,
        description="Existing candidate evidence found, if any (e.g. related technology or internship)",
    )
    suggested_actions: list[str] = Field(
        default_factory=list,
        description="Concrete practical action steps to achieve or demonstrate competency",
    )
    estimated_effort: str | None = Field(
        default=None,
        description="Defensible estimated effort or timeframe (e.g. 1-2 weeks, 2-4 weeks, Ongoing)",
    )
    source_component: str = Field(
        description="Source matching engine component: skill, experience, or education",
    )


class JobDescriptionRequest(BaseModel):
    """Incoming request payload to parse JD or match against candidate profile."""

    job_description: str = Field(
        ...,
        description="Full text of the target job description",
    )
    job_title: str | None = Field(
        default=None,
        description="Optional job title if known",
    )
    company: str | None = Field(
        default=None,
        description="Optional company name",
    )
    location: str | None = Field(
        default=None,
        description="Optional location or work mode",
    )
    file_id: str | None = Field(
        default=None,
        description="Optional 32-character hexadecimal UUID of an already-uploaded candidate resume",
    )

    @field_validator("job_description")
    @classmethod
    def validate_job_description(cls, value: str) -> str:
        """Validate that the job description contains meaningful text within bounds."""
        if not value or not value.strip():
            raise ValueError("Job description cannot be empty or whitespace.")

        cleaned = value.strip()
        if len(cleaned) < 50:
            raise ValueError(
                "Job description is too short (minimum 50 characters required for meaningful analysis)."
            )

        if len(cleaned) > 30000:
            raise ValueError(
                "Job description exceeds maximum allowed length of 30,000 characters."
            )

        # Ensure text is not just repeated punctuation/whitespace
        words = [w for w in cleaned.split() if any(c.isalnum() for c in w)]
        if len(words) < 8:
            raise ValueError(
                "Job description does not contain enough recognizable words to parse requirements."
            )

        return cleaned


class JobMatchRequest(JobDescriptionRequest):
    """Matching request payload requiring an uploaded resume file_id."""

    file_id: str = Field(
        ...,
        description="Required 32-character hexadecimal UUID of an already-uploaded candidate resume",
    )


class CandidateMatchSummary(BaseModel):
    """Safe candidate summary avoiding sensitive PII disclosure."""

    total_skills_count: int = Field(default=0, description="Total technical skills in profile")
    professional_experience_years: float | None = Field(
        default=None, description="Verified professional work experience years"
    )
    highest_degree: str | None = Field(default=None, description="Highest degree attained")
    projects_count: int = Field(default=0, description="Number of portfolio projects")


class MatchAnalysisMetadata(BaseModel):
    """Execution metadata for the job matching analysis."""

    timestamp: str = Field(description="ISO-8601 timestamp of analysis")
    engine_version: str = Field(default="5.6.0", description="CareerMind Matching Engine version")
    scoring_weights: dict[str, float] = Field(
        default_factory=dict, description="Scoring weights applied during assessment"
    )
    components_assessed: list[str] = Field(
        default_factory=list, description="Names of all evaluated components"
    )


class JobMatchResponse(BaseModel):
    """Consolidated API response for POST /api/v1/jobs/match."""

    success: bool = True
    file_id: str = Field(
        description="Unique 32-character hexadecimal identifier of matched resume"
    )
    parsed_job: ParsedJobDescription = Field(
        description="Structured representation of the analyzed job posting",
    )
    candidate_summary: CandidateMatchSummary = Field(
        default_factory=CandidateMatchSummary,
        description="Safe summary of candidate profile without sensitive PII",
    )
    match_score: MatchScoreBreakdown | None = Field(
        default=None,
        description="Explainable match score and component breakdown",
    )
    overall_score: float | None = Field(
        default=None,
        description="Aggregated match score between 0.0 and 100.0, or None if not assessable",
    )
    match_classification: str | None = Field(
        default=None,
        description="Classification: Strong Match, Moderate Match, Partial Match, Low Match, or Not assessable",
    )
    matched_skills: list[SkillMatchItem] = Field(
        default_factory=list,
        description="Detailed evaluation of all JD skills against candidate evidence",
    )
    related_skills: list[SkillMatchItem] = Field(
        default_factory=list,
        description="Skills identified as semantically related or transferable",
    )
    missing_required_skills: list[str] = Field(
        default_factory=list,
        description="Mandatory JD skills not found in candidate profile",
    )
    missing_preferred_skills: list[str] = Field(
        default_factory=list,
        description="Preferred JD skills not found in candidate profile",
    )
    experience_match: ExperienceMatchResult | None = Field(
        default=None,
        description="Detailed evaluation of professional, internship, and project experience",
    )
    education_match: EducationMatchResult | None = Field(
        default=None,
        description="Detailed evaluation of educational qualifications and disciplines",
    )
    recommendations: list[ActionableRecommendation] = Field(
        default_factory=list,
        description="Prioritized, actionable learning steps based on missing requirements",
    )
    metadata: MatchAnalysisMetadata | None = Field(
        default=None,
        description="Analysis execution metadata, engine version, and applied weights",
    )

