"""
Interview Session Service for AI Mock Interview Simulator (Phase 5).
Manages lifecycle of mock interview sessions: configuration, question selection,
answer evaluation, sequential progression, report generation, history listing, and deletion.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
import uuid

from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from database.models.career_profile import CareerProfile
from database.models.resume_record import ResumeRecord
from database.models.skill_gap_report import SkillGapReport
from database.models.interview_session import InterviewSession
from database.models.interview_session_question import InterviewSessionQuestion
from database.models.interview_answer import InterviewAnswer
from database.models.interview_evaluation import InterviewEvaluation
from database.models.interview_report import InterviewReport

from services.role_benchmark_service import ROLE_CATALOG
from services.interview_question_catalog import (
    QUESTION_BANK,
    QuestionItem,
    get_question_by_id,
)
from services.answer_evaluation_service import evaluate_answer
from services.interview_report_service import generate_interview_report
from schemas.interview_schema import (
    InterviewRoleOption,
    InterviewTypeOption,
    InterviewDifficultyOption,
    InterviewMetadataResponse,
    InterviewSessionCreateRequest,
)


# =============================================================================
# Custom Service Exceptions
# =============================================================================


class InterviewServiceError(Exception):
    """Base exception for interview service operations."""
    pass


class InterviewSessionNotFoundError(InterviewServiceError):
    """Raised when an interview session is not found."""
    pass


class InterviewQuestionNotFoundError(InterviewServiceError):
    """Raised when an interview question is not found in the active session."""
    pass


class InterviewSessionStateError(InterviewServiceError):
    """Raised when an operation is invalid for current session state."""
    pass


class DuplicateAnswerError(InterviewServiceError):
    """Raised when an answer is submitted for an already-answered question."""
    pass


class InvalidInterviewConfigurationError(InterviewServiceError):
    """Raised when input parameters for creating a session are invalid."""
    pass


# =============================================================================
# Metadata
# =============================================================================


def get_interview_metadata() -> InterviewMetadataResponse:
    """Return catalog metadata for configuring a mock interview session."""
    roles = [
        InterviewRoleOption(
            role_id=role.role_id,
            title=role.title,
            description=role.description,
        )
        for role in ROLE_CATALOG.values()
    ]

    interview_types = [
        InterviewTypeOption(
            type_id="technical",
            title="Technical Interview",
            description="Deep-dive into core computer science concepts, system architecture, programming languages, and framework specifics.",
        ),
        InterviewTypeOption(
            type_id="behavioral",
            title="HR & Behavioral Interview",
            description="Competency questions evaluated on the STAR rubric (Situation, Task, Action, Result), leadership, and collaboration.",
        ),
        InterviewTypeOption(
            type_id="project",
            title="Project-Based Interview",
            description="Practical architecture, system design trade-offs, debugging scenarios, and engineering decision-making.",
        ),
        InterviewTypeOption(
            type_id="mixed",
            title="Mixed Interview",
            description="Balanced comprehensive assessment blending technical fundamentals, project architecture, and behavioral dynamics.",
        ),
    ]

    difficulties = [
        InterviewDifficultyOption(
            difficulty_id="beginner",
            title="Beginner / Junior",
            description="Foundational core concepts, basic data structures, syntax, and fundamental definitions.",
        ),
        InterviewDifficultyOption(
            difficulty_id="intermediate",
            title="Intermediate / Mid-level",
            description="Practical applications, asynchronous programming, concurrency, index optimization, and architectural trade-offs.",
        ),
        InterviewDifficultyOption(
            difficulty_id="advanced",
            title="Advanced / Senior",
            description="High-scale distributed systems, low-level concurrency, compiler internals, performance profiling, and fault tolerance.",
        ),
    ]

    question_counts = [5, 10, 15, 20]

    # Collect unique categories across catalog
    categories = sorted(list({q.category for q in QUESTION_BANK}))

    return InterviewMetadataResponse(
        roles=roles,
        interview_types=interview_types,
        difficulties=difficulties,
        question_counts=question_counts,
        categories=categories,
    )


# =============================================================================
# Question Selection Engine
# =============================================================================


def select_questions_for_interview(
    target_role: str,
    interview_type: str,
    difficulty: str,
    count: int,
    gap_skills: Optional[List[str]] = None,
) -> List[QuestionItem]:
    """
    Select an optimal, non-repeating set of curated questions tailored to
    target role, interview format, difficulty, and candidate skill gaps.
    """
    target_role_norm = target_role.lower().strip()
    interview_type_norm = interview_type.lower().strip()
    difficulty_norm = difficulty.lower().strip()
    gap_skills_lower = [s.lower().strip() for s in (gap_skills or []) if s]

    # Map related roles for broader compatibility
    related_role_map = {
        "python_developer": ["backend_developer", "sde"],
        "backend_developer": ["python_developer", "sde", "full_stack_developer"],
        "frontend_developer": ["full_stack_developer", "sde"],
        "full_stack_developer": ["frontend_developer", "backend_developer", "sde"],
        "machine_learning_engineer": ["data_scientist", "python_developer"],
        "data_scientist": ["machine_learning_engineer", "data_analytics", "data_analyst"],
        "data_analyst": ["data_scientist"],
        "sde": ["backend_developer", "full_stack_developer"],
    }
    allowed_roles = {target_role_norm, "all"}
    for rel in related_role_map.get(target_role_norm, []):
        allowed_roles.add(rel)

    def is_role_applicable(q: QuestionItem) -> bool:
        return any(r in allowed_roles for r in q.applicable_roles)

    def score_question(q: QuestionItem) -> float:
        score = 0.0

        # 1. Skill Gap Boost (+100)
        if gap_skills_lower:
            q_skill_lower = q.relevant_skill.lower()
            q_concepts_lower = [c.lower() for c in q.expected_concepts]
            for gs in gap_skills_lower:
                if gs in q_skill_lower or q_skill_lower in gs:
                    score += 100.0
                    break
                if any(gs in c or c in gs for c in q_concepts_lower):
                    score += 50.0
                    break

        # 2. Difficulty Match (+50 exact, +20 adjacent)
        if q.difficulty == difficulty_norm:
            score += 50.0
        elif (difficulty_norm == "intermediate" and q.difficulty in ("beginner", "advanced")) or \
             (difficulty_norm in ("beginner", "advanced") and q.difficulty == "intermediate"):
            score += 20.0

        # 3. Exact Role Match (+25)
        if target_role_norm in q.applicable_roles:
            score += 25.0
        elif "all" in q.applicable_roles:
            score += 10.0

        return score

    selected_questions: List[QuestionItem] = []
    selected_ids = set()

    if interview_type_norm == "mixed":
        # Target balanced distribution: ~60% technical, ~20% project, ~20% behavioral
        target_tech = max(1, int(round(count * 0.60)))
        target_behav = max(1, int(round(count * 0.20)))
        target_proj = max(1, count - target_tech - target_behav)

        def pick_subset(i_type: str, needed: int) -> List[QuestionItem]:
            candidates = [
                q for q in QUESTION_BANK
                if q.interview_type == i_type and q.question_id not in selected_ids and is_role_applicable(q)
            ]
            candidates.sort(key=score_question, reverse=True)
            chosen = candidates[:needed]
            for c in chosen:
                selected_ids.add(c.question_id)
            return chosen

        selected_questions.extend(pick_subset("technical", target_tech))
        selected_questions.extend(pick_subset("behavioral", target_behav))
        selected_questions.extend(pick_subset("project", target_proj))

    else:
        # Strict interview type
        candidates = [
            q for q in QUESTION_BANK
            if q.interview_type == interview_type_norm and is_role_applicable(q)
        ]
        candidates.sort(key=score_question, reverse=True)
        for c in candidates[:count]:
            selected_questions.append(c)
            selected_ids.add(c.question_id)

    # Fallback: If still under requested count, relax role filter but respect interview type
    if len(selected_questions) < count:
        remaining_needed = count - len(selected_questions)
        fallback_candidates = [
            q for q in QUESTION_BANK
            if q.question_id not in selected_ids and
            (interview_type_norm == "mixed" or q.interview_type == interview_type_norm)
        ]
        fallback_candidates.sort(key=score_question, reverse=True)
        for c in fallback_candidates[:remaining_needed]:
            selected_questions.append(c)
            selected_ids.add(c.question_id)

    # Second Fallback: If catalog is still insufficient for the requested type (e.g. 20 project questions),
    # pull from any other available question to satisfy count without crashing
    if len(selected_questions) < count:
        remaining_needed = count - len(selected_questions)
        any_candidates = [
            q for q in QUESTION_BANK
            if q.question_id not in selected_ids
        ]
        any_candidates.sort(key=score_question, reverse=True)
        for c in any_candidates[:remaining_needed]:
            selected_questions.append(c)
            selected_ids.add(c.question_id)

    return selected_questions


# =============================================================================
# Session Lifecycle Service
# =============================================================================


def start_interview_session(
    db: Session,
    career_profile_id: str,
    request: InterviewSessionCreateRequest,
) -> InterviewSession:
    """Create and configure a new persistent interview session."""
    # 1. Validate Target Role
    role_norm = request.target_role.lower().strip()
    if role_norm not in ROLE_CATALOG:
        raise InvalidInterviewConfigurationError(
            f"Target role '{request.target_role}' is not supported. Supported roles: {list(ROLE_CATALOG.keys())}"
        )
    role_benchmark = ROLE_CATALOG[role_norm]

    # 2. Validate Type & Difficulty
    valid_types = {"technical", "behavioral", "project", "mixed"}
    if request.interview_type.lower() not in valid_types:
        raise InvalidInterviewConfigurationError(
            f"Invalid interview type '{request.interview_type}'. Supported: {sorted(list(valid_types))}"
        )

    valid_difficulties = {"beginner", "intermediate", "advanced"}
    if request.difficulty.lower() not in valid_difficulties:
        raise InvalidInterviewConfigurationError(
            f"Invalid difficulty '{request.difficulty}'. Supported: {sorted(list(valid_difficulties))}"
        )

    # 3. Validate Resume if provided
    if request.resume_id:
        resume = db.execute(
            select(ResumeRecord).where(
                ResumeRecord.id == request.resume_id,
                ResumeRecord.career_profile_id == career_profile_id,
            )
        ).scalar_one_or_none()
        if not resume:
            raise InvalidInterviewConfigurationError(
                f"Resume record '{request.resume_id}' not found for this candidate."
            )

    # 4. Validate & Extract Skill Gap Report if provided
    gap_skills: List[str] = []
    if request.skill_gap_report_id:
        gap_report = db.execute(
            select(SkillGapReport).where(
                SkillGapReport.id == request.skill_gap_report_id,
                SkillGapReport.career_profile_id == career_profile_id,
            )
        ).scalar_one_or_none()
        if not gap_report:
            raise InvalidInterviewConfigurationError(
                f"Skill Gap Report '{request.skill_gap_report_id}' not found for this candidate."
            )
        
        # Extract missing required and preferred skills
        for item in (gap_report.missing_required_skills or []):
            if isinstance(item, dict):
                gap_skills.append(item.get("skill_name") or item.get("skill") or "")
            elif isinstance(item, str):
                gap_skills.append(item)
        for item in (gap_report.related_skills or []):
            if isinstance(item, dict):
                gap_skills.append(item.get("benchmark_skill") or item.get("skill") or "")
            elif isinstance(item, str):
                gap_skills.append(item)

    # 5. Select Questions
    selected_questions = select_questions_for_interview(
        target_role=role_norm,
        interview_type=request.interview_type,
        difficulty=request.difficulty,
        count=request.question_count,
        gap_skills=gap_skills,
    )

    if not selected_questions:
        raise InterviewServiceError("Unable to select questions for the specified interview criteria.")

    # 6. Create Persistent Session
    session = InterviewSession(
        career_profile_id=career_profile_id,
        resume_record_id=request.resume_id,
        skill_gap_report_id=request.skill_gap_report_id,
        target_role=role_norm,
        role_title=role_benchmark.title,
        interview_type=request.interview_type.lower(),
        difficulty=request.difficulty.lower(),
        total_questions=len(selected_questions),
        current_question_index=0,
        status="in_progress",
    )
    db.add(session)
    db.flush()

    # 7. Add Questions as Snapshots
    for idx, q in enumerate(selected_questions):
        session_question = InterviewSessionQuestion(
            session_id=session.id,
            sequence_order=idx + 1,
            question_bank_id=q.question_id,
            question_text=q.question_text,
            category=q.category,
            interview_type=q.interview_type,
            difficulty=q.difficulty,
            relevant_skill=q.relevant_skill,
            expected_concepts=q.expected_concepts,
            suggested_answer_points=q.suggested_answer_points,
            evaluation_rubric=q.evaluation_rubric,
            weight=q.weight,
            is_answered=False,
        )
        db.add(session_question)

    db.commit()
    db.refresh(session)
    return session


def get_interview_session(
    db: Session,
    career_profile_id: str,
    session_id: str,
) -> InterviewSession:
    """Retrieve an interview session by ID ensuring candidate ownership."""
    stmt = (
        select(InterviewSession)
        .where(
            InterviewSession.id == session_id,
            InterviewSession.career_profile_id == career_profile_id,
        )
    )
    session = db.execute(stmt).scalar_one_or_none()
    if not session:
        raise InterviewSessionNotFoundError(
            f"Interview session '{session_id}' not found."
        )
    return session


def get_current_question(
    db: Session,
    career_profile_id: str,
    session_id: str,
) -> Optional[InterviewSessionQuestion]:
    """Retrieve the currently active unanswered question for a session."""
    session = get_interview_session(db, career_profile_id, session_id)
    if session.status != "in_progress":
        return None

    unanswered = [q for q in session.questions if not q.is_answered]
    if not unanswered:
        return None

    return unanswered[0]


def submit_answer(
    db: Session,
    career_profile_id: str,
    session_id: str,
    session_question_id: str,
    answer_text: str,
) -> Tuple[InterviewAnswer, InterviewEvaluation]:
    """Submit candidate response to a question, run evaluation, and update session progression."""
    session = get_interview_session(db, career_profile_id, session_id)
    if session.status != "in_progress":
        raise InterviewSessionStateError(
            f"Cannot submit answer: interview session is currently '{session.status}'."
        )

    # Locate question within this session
    target_question: Optional[InterviewSessionQuestion] = None
    for q in session.questions:
        if q.id == session_question_id:
            target_question = q
            break

    if not target_question:
        raise InterviewQuestionNotFoundError(
            f"Question '{session_question_id}' does not belong to session '{session_id}'."
        )

    if target_question.is_answered:
        raise DuplicateAnswerError(
            "This question has already been answered. Duplicate submissions are not permitted."
        )

    # Evaluate Answer using Deterministic Rubric
    cleaned_text = (answer_text or "").strip()
    eval_result = evaluate_answer(
        answer_text=cleaned_text,
        question_text=target_question.question_text,
        expected_concepts=target_question.expected_concepts,
        suggested_answer_points=target_question.suggested_answer_points,
        evaluation_rubric=target_question.evaluation_rubric,
        interview_type=target_question.interview_type,
        difficulty=target_question.difficulty,
    )

    # Persist Answer
    answer = InterviewAnswer(
        session_id=session.id,
        session_question_id=target_question.id,
        answer_text=cleaned_text,
    )
    db.add(answer)
    db.flush()

    # Persist Evaluation
    evaluation = InterviewEvaluation(
        answer_id=answer.id,
        overall_score=eval_result.overall_score,
        relevance_score=eval_result.relevance_score,
        concept_coverage_score=eval_result.concept_coverage_score,
        completeness_score=eval_result.completeness_score,
        structure_score=eval_result.structure_score,
        identified_concepts=eval_result.identified_concepts,
        missing_concepts=eval_result.missing_concepts,
        strengths=eval_result.strengths,
        improvement_suggestions=eval_result.improvement_suggestions,
        evaluator_method=eval_result.evaluator_method,
        feedback_rationale=eval_result.feedback_rationale,
    )
    db.add(evaluation)

    # Mark question as answered
    target_question.is_answered = True
    session.current_question_index = min(session.total_questions, session.current_question_index + 1)

    db.commit()
    db.refresh(answer)
    db.refresh(evaluation)
    return answer, evaluation


def complete_interview_session(
    db: Session,
    career_profile_id: str,
    session_id: str,
) -> InterviewReport:
    """Finalize an interview session and generate the persistent performance report."""
    session = get_interview_session(db, career_profile_id, session_id)
    report = generate_interview_report(db, session)
    return report


def get_interview_report(
    db: Session,
    career_profile_id: str,
    session_id: str,
) -> InterviewReport:
    """Fetch the performance report for a session, generating it if not yet compiled."""
    session = get_interview_session(db, career_profile_id, session_id)
    if session.report:
        return session.report
    return generate_interview_report(db, session)


def list_interview_sessions(
    db: Session,
    career_profile_id: str,
) -> List[InterviewSession]:
    """List all interview sessions for the candidate ordered by creation time descending."""
    stmt = (
        select(InterviewSession)
        .where(InterviewSession.career_profile_id == career_profile_id)
        .order_by(desc(InterviewSession.created_at))
    )
    return list(db.execute(stmt).scalars().all())


def delete_interview_session(
    db: Session,
    career_profile_id: str,
    session_id: str,
) -> bool:
    """Delete an interview session and cascade delete all its questions, answers, and report."""
    session = get_interview_session(db, career_profile_id, session_id)
    db.delete(session)
    db.commit()
    return True

