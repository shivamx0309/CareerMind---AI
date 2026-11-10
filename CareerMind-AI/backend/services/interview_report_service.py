"""
Interview Report Service for AI Mock Interview Simulator.
Compiles comprehensive post-session performance evaluations, category breakdowns,
frequently missed concepts, and actionable study recommendations.
"""

from collections import Counter
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid

from sqlalchemy.orm import Session

from database.models.interview_session import InterviewSession
from database.models.interview_report import InterviewReport


def generate_interview_report(
    db: Session,
    session: InterviewSession,
) -> InterviewReport:
    """
    Generate or recalculate the persistent InterviewReport for a completed session.
    """
    total_questions = len(session.questions)
    answered_questions = [q for q in session.questions if q.is_answered and q.answer and q.answer.evaluation]
    questions_attempted = len(answered_questions)

    # 1. Calculate Scores
    if questions_attempted > 0:
        scores = [q.answer.evaluation.overall_score for q in answered_questions]
        average_score = round(sum(scores) / questions_attempted, 1)
        # Weighted overall score based on total questions in session
        overall_score = round((sum(scores) / max(1, total_questions)), 1)
    else:
        average_score = 0.0
        overall_score = 0.0

    # 2. Category Level Breakdown
    categories_map: Dict[str, List[float]] = {}
    for q in session.questions:
        cat = q.category
        if cat not in categories_map:
            categories_map[cat] = []
        if q.is_answered and q.answer and q.answer.evaluation:
            categories_map[cat].append(q.answer.evaluation.overall_score)

    category_scores: Dict[str, Dict[str, Any]] = {}
    strong_areas: List[str] = []
    weak_areas: List[str] = []
    recommended_topics: List[str] = []

    for cat, cat_scores in categories_map.items():
        if cat_scores:
            cat_avg = round(sum(cat_scores) / len(cat_scores), 1)
            category_scores[cat] = {
                "average_score": cat_avg,
                "attempted": len(cat_scores),
                "total": len([q for q in session.questions if q.category == cat]),
                "status": "assessed",
            }
            formatted_cat = cat.replace("_", " ").title()
            if cat_avg >= 75.0:
                strong_areas.append(f"{formatted_cat} ({cat_avg}%)")
            elif cat_avg < 60.0:
                weak_areas.append(f"{formatted_cat} ({cat_avg}%)")
                recommended_topics.append(formatted_cat)
        else:
            category_scores[cat] = {
                "average_score": None,
                "attempted": 0,
                "total": len([q for q in session.questions if q.category == cat]),
                "status": "insufficient_data",
            }

    # 3. Frequently Missed Concepts
    missed_counter: Counter = Counter()
    for q in answered_questions:
        for mc in q.answer.evaluation.missing_concepts:
            missed_counter[mc] += 1

    frequently_missed = [concept for concept, _ in missed_counter.most_common(5)]

    # 4. Actionable Feedback Aggregation
    actionable_feedback: List[str] = []
    for q in answered_questions:
        for sugg in q.answer.evaluation.improvement_suggestions:
            if sugg not in actionable_feedback and len(actionable_feedback) < 6:
                actionable_feedback.append(sugg)

    if not actionable_feedback:
        actionable_feedback.append("Practice explaining technical trade-offs with concrete code or system architecture examples.")

    # 5. Performance Summary
    performance_summary = (
        f"Mock Interview completed for role '{session.role_title}' ({session.interview_type.title()} Interview, {session.difficulty.title()} level). "
        f"You attempted {questions_attempted} of {total_questions} questions with an average answer score of {average_score}%. "
        f"Overall assessment score: {overall_score}%. "
        f"Disclaimer: This feedback is generated via explainable rubric-based heuristics for targeted practice and self-assessment; "
        f"it does not guarantee hiring success or replace subjective human interviewer judgment."
    )

    # 6. Check if Report already exists (Upsert)
    if session.report:
        report = session.report
        report.overall_score = overall_score
        report.questions_attempted = questions_attempted
        report.total_questions = total_questions
        report.average_answer_score = average_score
        report.category_scores = category_scores
        report.strong_areas = strong_areas
        report.weak_areas = weak_areas
        report.frequently_missed_concepts = frequently_missed
        report.recommended_topics = recommended_topics
        report.actionable_feedback = actionable_feedback
        report.performance_summary = performance_summary
    else:
        report = InterviewReport(
            session_id=session.id,
            overall_score=overall_score,
            questions_attempted=questions_attempted,
            total_questions=total_questions,
            average_answer_score=average_score,
            category_scores=category_scores,
            strong_areas=strong_areas,
            weak_areas=weak_areas,
            frequently_missed_concepts=frequently_missed,
            recommended_topics=recommended_topics,
            actionable_feedback=actionable_feedback,
            performance_summary=performance_summary,
        )
        db.add(report)

    # Update session status and score
    session.overall_score = overall_score
    session.performance_summary = performance_summary
    session.status = "completed"
    session.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(report)
    return report

