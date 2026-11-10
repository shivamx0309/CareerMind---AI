"""
Pydantic schemas for the AI Mock Interview Simulator Engine (Phase 5).
Defines schemas for configuration metadata, session lifecycle, questions,
answers, rubric-based evaluations, and final interview reports.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class InterviewRoleOption(BaseModel):
    """Supported target role option with human-readable description."""

    role_id: str
    title: str
    description: str


class InterviewTypeOption(BaseModel):
    """Interview format option."""

    type_id: str
    title: str
    description: str


class InterviewDifficultyOption(BaseModel):
    """Target difficulty level option."""

    difficulty_id: str
    title: str
    description: str


class InterviewMetadataResponse(BaseModel):
    """Catalog metadata for configuring a mock interview session."""

    roles: List[InterviewRoleOption]
    interview_types: List[InterviewTypeOption]
    difficulties: List[InterviewDifficultyOption]
    question_counts: List[int]
    categories: List[str]


class InterviewSessionCreateRequest(BaseModel):
    """Payload to configure and initiate a new mock interview session."""

    target_role: str = Field(..., description="Target role identifier (e.g. sde, frontend_developer)")
    interview_type: str = Field(
        default="technical",
        description="Interview type: technical, behavioral, project, or mixed",
    )
    difficulty: str = Field(
        default="intermediate",
        description="Difficulty tier: beginner, intermediate, or advanced",
    )
    question_count: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of questions to ask (e.g. 5, 10, 15, 20)",
    )
    resume_id: Optional[str] = Field(
        default=None,
        description="Optional ResumeRecord ID to tie interview to existing resume",
    )
    skill_gap_report_id: Optional[str] = Field(
        default=None,
        description="Optional SkillGapReport ID to prioritize candidate's missing/related skills",
    )


class SessionQuestionResponse(BaseModel):
    """
    Public question view presented to candidate during active interview.
    Answer keys, expected concepts, and grading rubrics are strictly withheld.
    """

    id: str
    session_id: str
    sequence_order: int
    question_bank_id: str
    question_text: str
    category: str
    interview_type: str
    difficulty: str
    relevant_skill: str
    weight: float
    is_answered: bool

    model_config = ConfigDict(from_attributes=True)


class AnswerSubmitRequest(BaseModel):
    """Payload when a candidate submits an answer to a question."""

    question_id: Optional[str] = Field(
        default=None,
        description="Optional session question ID. If omitted, targets the active unanswered question.",
    )
    answer_text: str = Field(..., description="Candidate's typed response text")


class AnswerEvaluationResponse(BaseModel):
    """Explainable evaluation scores and rubric feedback for a submitted answer."""

    id: str
    answer_id: str
    overall_score: float
    relevance_score: float
    concept_coverage_score: float
    completeness_score: float
    structure_score: float
    identified_concepts: List[str]
    missing_concepts: List[str]
    strengths: List[str]
    improvement_suggestions: List[str]
    evaluator_method: str
    feedback_rationale: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InterviewAnswerResponse(BaseModel):
    """Submitted answer record with associated evaluation feedback."""

    id: str
    session_id: str
    session_question_id: str
    answer_text: str
    submitted_at: datetime
    evaluation: Optional[AnswerEvaluationResponse] = None

    model_config = ConfigDict(from_attributes=True)


class SessionQuestionDetailResponse(BaseModel):
    """Detailed question representation showing answer and evaluation if answered."""

    id: str
    session_id: str
    sequence_order: int
    question_bank_id: str
    question_text: str
    category: str
    interview_type: str
    difficulty: str
    relevant_skill: str
    weight: float
    is_answered: bool
    suggested_answer_points: Optional[List[str]] = None
    answer: Optional[InterviewAnswerResponse] = None

    model_config = ConfigDict(from_attributes=True)


class InterviewSessionResponse(BaseModel):
    """Full interview session representation."""

    id: str
    career_profile_id: str
    resume_record_id: Optional[str] = None
    skill_gap_report_id: Optional[str] = None
    target_role: str
    role_title: str
    interview_type: str
    difficulty: str
    total_questions: int
    current_question_index: int
    status: str
    overall_score: Optional[float] = None
    performance_summary: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    created_at: datetime
    questions: List[SessionQuestionDetailResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class InterviewSessionSummaryResponse(BaseModel):
    """Compact summary of an interview session for list views."""

    id: str
    target_role: str
    role_title: str
    interview_type: str
    difficulty: str
    total_questions: int
    questions_answered: int
    status: str
    overall_score: Optional[float] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class InterviewReportResponse(BaseModel):
    """Final comprehensive performance report for a completed session."""

    id: str
    session_id: str
    overall_score: float
    questions_attempted: int
    total_questions: int
    average_answer_score: float
    category_scores: Dict[str, Any]
    strong_areas: List[str]
    weak_areas: List[str]
    frequently_missed_concepts: List[str]
    recommended_topics: List[str]
    actionable_feedback: List[str]
    performance_summary: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
