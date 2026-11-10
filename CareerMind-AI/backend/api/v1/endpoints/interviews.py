"""
Mock Interview API Endpoints (Phase 5).
Provides endpoints for interview session configuration, progressive question retrieval,
rubric-based answer evaluation, session completion, comprehensive performance reporting,
history listing, and cascade deletion.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.session import get_db
from database.models.interview_session import InterviewSession
from database.models.interview_session_question import InterviewSessionQuestion
from schemas.interview_schema import (
    InterviewMetadataResponse,
    InterviewSessionCreateRequest,
    InterviewSessionResponse,
    InterviewSessionSummaryResponse,
    SessionQuestionResponse,
    SessionQuestionDetailResponse,
    AnswerSubmitRequest,
    InterviewAnswerResponse,
    AnswerEvaluationResponse,
    InterviewReportResponse,
)
from services import (
    career_profile_service,
    interview_session_service,
)
from services.interview_session_service import (
    InterviewServiceError,
    InterviewSessionNotFoundError,
    InterviewQuestionNotFoundError,
    InterviewSessionStateError,
    DuplicateAnswerError,
    InvalidInterviewConfigurationError,
)

router = APIRouter(
    prefix="/interviews",
    tags=["Mock Interview Simulator"],
)


def _format_session_response(session: InterviewSession) -> InterviewSessionResponse:
    """Format an InterviewSession entity, strictly hiding secret rubrics/points for unanswered questions."""
    formatted_questions: List[SessionQuestionDetailResponse] = []

    for q in session.questions:
        if q.is_answered and q.answer:
            answer_dto = InterviewAnswerResponse(
                id=q.answer.id,
                session_id=q.answer.session_id,
                session_question_id=q.answer.session_question_id,
                answer_text=q.answer.answer_text,
                submitted_at=q.answer.submitted_at,
                evaluation=(
                    AnswerEvaluationResponse.model_validate(q.answer.evaluation)
                    if q.answer.evaluation
                    else None
                ),
            )
            suggested_points = q.suggested_answer_points
        else:
            answer_dto = None
            suggested_points = None

        formatted_questions.append(
            SessionQuestionDetailResponse(
                id=q.id,
                session_id=q.session_id,
                sequence_order=q.sequence_order,
                question_bank_id=q.question_bank_id,
                question_text=q.question_text,
                category=q.category,
                interview_type=q.interview_type,
                difficulty=q.difficulty,
                relevant_skill=q.relevant_skill,
                weight=q.weight,
                is_answered=q.is_answered,
                suggested_answer_points=suggested_points,
                answer=answer_dto,
            )
        )

    return InterviewSessionResponse(
        id=session.id,
        career_profile_id=session.career_profile_id,
        resume_record_id=session.resume_record_id,
        skill_gap_report_id=session.skill_gap_report_id,
        target_role=session.target_role,
        role_title=session.role_title,
        interview_type=session.interview_type,
        difficulty=session.difficulty,
        total_questions=session.total_questions,
        current_question_index=session.current_question_index,
        status=session.status,
        overall_score=session.overall_score,
        performance_summary=session.performance_summary,
        started_at=session.started_at,
        completed_at=session.completed_at,
        created_at=session.created_at,
        questions=formatted_questions,
    )


# =============================================================================
# 1. Metadata & Configuration
# =============================================================================


@router.get(
    "/metadata",
    response_model=InterviewMetadataResponse,
    status_code=status.HTTP_200_OK,
    summary="Get interview catalog metadata",
    description="Retrieve supported roles, interview formats, difficulty levels, question counts, and question categories.",
)
def get_interview_metadata():
    """Retrieve metadata for configuring an interview session."""
    return interview_session_service.get_interview_metadata()


# =============================================================================
# 2. Session Management
# =============================================================================


@router.post(
    "/sessions",
    response_model=InterviewSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new mock interview session",
    description="Configure and start a new interview session. Questions are dynamically selected without revealing answer keys.",
)
def start_interview_session(
    request: InterviewSessionCreateRequest,
    db: Session = Depends(get_db),
):
    """Initiate a persistent interview session."""
    profile = career_profile_service.get_or_create_local_career_profile(db)
    try:
        session = interview_session_service.start_interview_session(
            db=db,
            career_profile_id=profile.id,
            request=request,
        )
        return _format_session_response(session)
    except InvalidInterviewConfigurationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except InterviewServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/sessions",
    response_model=List[InterviewSessionSummaryResponse],
    status_code=status.HTTP_200_OK,
    summary="List interview history",
    description="Retrieve all previous interview sessions for the local candidate, ordered by newest first.",
)
def list_interview_sessions(
    db: Session = Depends(get_db),
):
    """List mock interview history."""
    profile = career_profile_service.get_or_create_local_career_profile(db)
    sessions = interview_session_service.list_interview_sessions(db, profile.id)

    summaries = []
    for s in sessions:
        answered_count = len([q for q in s.questions if q.is_answered])
        summaries.append(
            InterviewSessionSummaryResponse(
                id=s.id,
                target_role=s.target_role,
                role_title=s.role_title,
                interview_type=s.interview_type,
                difficulty=s.difficulty,
                total_questions=s.total_questions,
                questions_answered=answered_count,
                status=s.status,
                overall_score=s.overall_score,
                started_at=s.started_at,
                completed_at=s.completed_at,
            )
        )
    return summaries


@router.get(
    "/sessions/{session_id}",
    response_model=InterviewSessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get interview session details",
    description="Retrieve detailed status and questions for a specific session.",
)
def get_interview_session(
    session_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve an interview session by ID."""
    profile = career_profile_service.get_or_create_local_career_profile(db)
    try:
        session = interview_session_service.get_interview_session(db, profile.id, session_id)
        return _format_session_response(session)
    except InterviewSessionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an interview session",
    description="Permanently delete an interview session and all its associated questions, answers, evaluations, and reports.",
)
def delete_interview_session(
    session_id: str,
    db: Session = Depends(get_db),
):
    """Delete an interview session."""
    profile = career_profile_service.get_or_create_local_career_profile(db)
    try:
        interview_session_service.delete_interview_session(db, profile.id, session_id)
        return None
    except InterviewSessionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# =============================================================================
# 3. Question Progression & Answering
# =============================================================================


@router.get(
    "/sessions/{session_id}/current-question",
    response_model=Optional[SessionQuestionResponse],
    status_code=status.HTTP_200_OK,
    summary="Get current active question",
    description="Fetch the next unanswered question for an active session. Withholds rubrics and answer keys.",
)
def get_current_question(
    session_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve the next unanswered question in sequence."""
    profile = career_profile_service.get_or_create_local_career_profile(db)
    try:
        question = interview_session_service.get_current_question(db, profile.id, session_id)
        if not question:
            return None
        return SessionQuestionResponse.model_validate(question)
    except InterviewSessionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    "/sessions/{session_id}/answer",
    response_model=InterviewAnswerResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit answer for evaluation",
    description="Submit candidate answer for the current or specified question. Evaluates deterministically against rubric.",
)
def submit_answer(
    session_id: str,
    payload: AnswerSubmitRequest,
    db: Session = Depends(get_db),
):
    """Submit an answer to an interview question."""
    profile = career_profile_service.get_or_create_local_career_profile(db)
    try:
        # Determine target question ID
        question_id = payload.question_id
        if not question_id:
            current_q = interview_session_service.get_current_question(db, profile.id, session_id)
            if not current_q:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="All questions in this session have already been answered.",
                )
            question_id = current_q.id

        answer, evaluation = interview_session_service.submit_answer(
            db=db,
            career_profile_id=profile.id,
            session_id=session_id,
            session_question_id=question_id,
            answer_text=payload.answer_text,
        )

        return InterviewAnswerResponse(
            id=answer.id,
            session_id=answer.session_id,
            session_question_id=answer.session_question_id,
            answer_text=answer.answer_text,
            submitted_at=answer.submitted_at,
            evaluation=AnswerEvaluationResponse.model_validate(evaluation),
        )
    except InterviewSessionNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InterviewQuestionNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InterviewSessionStateError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except DuplicateAnswerError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/sessions/{session_id}/questions/{question_id}/answer",
    response_model=InterviewAnswerResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit answer to a specific question",
    description="Explicitly submit candidate response to the specified session question.",
)
def submit_answer_to_question(
    session_id: str,
    question_id: str,
    payload: AnswerSubmitRequest,
    db: Session = Depends(get_db),
):
    """Explicit endpoint for submitting an answer to a specific question ID."""
    profile = career_profile_service.get_or_create_local_career_profile(db)
    try:
        answer, evaluation = interview_session_service.submit_answer(
            db=db,
            career_profile_id=profile.id,
            session_id=session_id,
            session_question_id=question_id,
            answer_text=payload.answer_text,
        )
        return InterviewAnswerResponse(
            id=answer.id,
            session_id=answer.session_id,
            session_question_id=answer.session_question_id,
            answer_text=answer.answer_text,
            submitted_at=answer.submitted_at,
            evaluation=AnswerEvaluationResponse.model_validate(evaluation),
        )
    except InterviewSessionNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InterviewQuestionNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InterviewSessionStateError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except DuplicateAnswerError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# =============================================================================
# 4. Session Completion & Report
# =============================================================================


@router.post(
    "/sessions/{session_id}/complete",
    response_model=InterviewReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Complete interview and generate report",
    description="Finalize session, calculate category breakdowns, strengths, weak areas, and generate persistent report.",
)
def complete_interview_session(
    session_id: str,
    db: Session = Depends(get_db),
):
    """Finalize an interview session."""
    profile = career_profile_service.get_or_create_local_career_profile(db)
    try:
        report = interview_session_service.complete_interview_session(db, profile.id, session_id)
        return InterviewReportResponse.model_validate(report)
    except InterviewSessionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/sessions/{session_id}/report",
    response_model=InterviewReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Get interview performance report",
    description="Retrieve the performance report for a session.",
)
def get_interview_report(
    session_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve the performance report for a session."""
    profile = career_profile_service.get_or_create_local_career_profile(db)
    try:
        report = interview_session_service.get_interview_report(db, profile.id, session_id)
        return InterviewReportResponse.model_validate(report)
    except InterviewSessionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

