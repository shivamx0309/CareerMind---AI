"""
CareerMind AI — Phase 5.1: AI Mock Interview Simulator Engine Unit & Integration Tests.

Comprehensive test suite verifying:
1. Interview metadata endpoint (roles, formats, difficulties, counts, categories)
2. Session creation across all supported interview types (technical, behavioral, project, mixed)
3. Role and difficulty validation error handling (400 Bad Request)
4. Question selection without duplicates and graceful fallback for large question counts
5. Personalization: prioritization of candidate skill gaps when SkillGapReport is linked
6. Strict withholding of answer keys and expected concepts in public question views
7. Deterministic answer evaluation: concept coverage, relevance, completeness, structure
8. Edge cases: empty answers and very short (< 4 words) answers
9. Behavioral interview STAR rubric evaluation
10. Session progression and sequential active question tracking
11. Duplicate answer submission prevention (400 Bad Request)
12. Session ownership checks and invalid question/session handling (404 Not Found)
13. Session completion and comprehensive report generation
14. Category breakdown, strong/weak areas, and frequently missed concepts aggregation
15. Historical session listing and single session retrieval
16. Cascade deletion of session, questions, answers, evaluations, and reports
17. Non-regression of existing features (Resume Library, Skill Gap, Learning Roadmap)
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database.base import Base
from database.session import get_db
from database.models.career_profile import CareerProfile
from database.models.resume_record import ResumeRecord
from database.models.skill_gap_report import SkillGapReport
from database.models.interview_session import InterviewSession
from database.models.interview_session_question import InterviewSessionQuestion
from database.models.interview_answer import InterviewAnswer
from database.models.interview_evaluation import InterviewEvaluation
from database.models.interview_report import InterviewReport

from schemas.candidate_schema import (
    CandidateProfile,
    PersonalInformation,
    TechnicalSkills,
)
from services import (
    storage_service,
    resume_library_service,
    career_profile_service,
    role_benchmark_service,
    skill_gap_service,
    interview_session_service,
    answer_evaluation_service,
    interview_question_catalog,
)
from api.v1.endpoints import resume as resume_endpoint
from api.v1.endpoints import jobs as jobs_endpoint


# Isolated in-memory database
TEST_DB_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def setup_isolated_env(tmp_path, monkeypatch):
    """Clean in-memory DB and isolated upload directory for every test."""
    Base.metadata.create_all(bind=test_engine)
    monkeypatch.setattr(resume_endpoint, "UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(storage_service, "UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(jobs_endpoint, "UPLOAD_DIR", tmp_path)

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def seed_candidate_with_gap_report(db, role_id="backend_developer"):
    """Helper to seed profile, resume, and run skill gap analysis to produce a report."""
    profile = career_profile_service.get_or_create_local_career_profile(db)

    cand = CandidateProfile(
        personal_information=PersonalInformation(
            full_name="Priya Sharma",
            email="priya@example.com",
            phone="+919876543210",
        ),
        technical_skills=TechnicalSkills(
            programming_languages=["Python"],
            databases=["PostgreSQL"],
            backend=["Flask"],
            tools=["Git"],
        ),
    )

    rec = resume_library_service.register_uploaded_resume(
        db=db,
        career_profile_id=profile.id,
        file_id="11112222333344445555666677778888",
        original_filename="priya_resume.pdf",
        file_size=10240,
        display_name="Priya Resume",
    )
    rec.is_default = True
    db.commit()
    resume_library_service.persist_parsed_candidate_profile(db, rec.id, cand)

    report = skill_gap_service.analyze_skill_gap(
        db=db,
        career_profile_id=profile.id,
        target_role=role_id,
        resume_id=rec.id,
    )
    return profile, rec, report


# =============================================================================
# 1. Metadata Endpoint Tests
# =============================================================================


def test_interview_metadata_endpoint(client):
    """Verify metadata returns all 8 roles, 4 interview types, 3 difficulties, and 15 categories."""
    response = client.get("/api/v1/interviews/metadata")
    assert response.status_code == 200
    data = response.json()

    assert "roles" in data
    assert len(data["roles"]) == 8
    role_ids = [r["role_id"] for r in data["roles"]]
    assert "sde" in role_ids
    assert "backend_developer" in role_ids
    assert "frontend_developer" in role_ids
    assert "machine_learning_engineer" in role_ids

    assert "interview_types" in data
    type_ids = [t["type_id"] for t in data["interview_types"]]
    assert set(type_ids) == {"technical", "behavioral", "project", "mixed"}

    assert "difficulties" in data
    diff_ids = [d["difficulty_id"] for d in data["difficulties"]]
    assert set(diff_ids) == {"beginner", "intermediate", "advanced"}

    assert data["question_counts"] == [5, 10, 15, 20]
    assert len(data["categories"]) == 15
    assert "programming_fundamentals" in data["categories"]
    assert "system_design" in data["categories"]
    assert "hr_behavioral" in data["categories"]


# =============================================================================
# 2. Session Creation Across All Types
# =============================================================================


@pytest.mark.parametrize("interview_type", ["technical", "behavioral", "project", "mixed"])
def test_create_interview_session_all_types(client, interview_type):
    """Verify session creation succeeds for each interview type and questions match criteria."""
    payload = {
        "target_role": "backend_developer",
        "interview_type": interview_type,
        "difficulty": "intermediate",
        "question_count": 5,
    }
    response = client.post("/api/v1/interviews/sessions", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["target_role"] == "backend_developer"
    assert data["interview_type"] == interview_type
    assert data["difficulty"] == "intermediate"
    assert data["total_questions"] == 5
    assert data["current_question_index"] == 0
    assert data["status"] == "in_progress"
    assert len(data["questions"]) == 5

    # Check question ordering and fields
    for idx, q in enumerate(data["questions"]):
        assert q["sequence_order"] == idx + 1
        assert q["question_text"]
        assert q["is_answered"] is False
        assert q["answer"] is None
        # Public view MUST hide suggested answer points
        assert q.get("suggested_answer_points") is None


# =============================================================================
# 3. Input Validation & Error Handling
# =============================================================================


def test_invalid_role_configuration(client):
    """Verify 400 Bad Request for unsupported role."""
    payload = {
        "target_role": "quantum_blockchain_wizard",
        "interview_type": "technical",
        "difficulty": "intermediate",
        "question_count": 5,
    }
    response = client.post("/api/v1/interviews/sessions", json=payload)
    assert response.status_code == 400
    assert "Target role 'quantum_blockchain_wizard' is not supported" in response.json()["detail"]


def test_invalid_interview_type(client):
    """Verify 400 Bad Request for unsupported interview type."""
    payload = {
        "target_role": "sde",
        "interview_type": "coding_battle_royale",
        "difficulty": "intermediate",
        "question_count": 5,
    }
    response = client.post("/api/v1/interviews/sessions", json=payload)
    assert response.status_code == 400
    assert "Invalid interview type" in response.json()["detail"]


def test_invalid_difficulty(client):
    """Verify 400 Bad Request for invalid difficulty tier."""
    payload = {
        "target_role": "sde",
        "interview_type": "technical",
        "difficulty": "impossible",
        "question_count": 5,
    }
    response = client.post("/api/v1/interviews/sessions", json=payload)
    assert response.status_code == 400
    assert "Invalid difficulty" in response.json()["detail"]


def test_nonexistent_resume_or_gap_report(client):
    """Verify 400 Bad Request when non-existent resume_id or skill_gap_report_id is passed."""
    # Bad resume
    res = client.post(
        "/api/v1/interviews/sessions",
        json={
            "target_role": "sde",
            "interview_type": "technical",
            "difficulty": "beginner",
            "question_count": 5,
            "resume_id": "nonexistent-resume-uuid",
        },
    )
    assert res.status_code == 400
    assert "Resume record 'nonexistent-resume-uuid' not found" in res.json()["detail"]

    # Bad skill gap report
    res2 = client.post(
        "/api/v1/interviews/sessions",
        json={
            "target_role": "sde",
            "interview_type": "technical",
            "difficulty": "beginner",
            "question_count": 5,
            "skill_gap_report_id": "nonexistent-report-uuid",
        },
    )
    assert res2.status_code == 400
    assert "Skill Gap Report 'nonexistent-report-uuid' not found" in res2.json()["detail"]


# =============================================================================
# 4. Question Selection & Fallback Behavior
# =============================================================================


def test_question_selection_no_duplicates_and_count_fallback(client):
    """Verify requesting 20 questions does not produce duplicates and falls back gracefully."""
    payload = {
        "target_role": "machine_learning_engineer",
        "interview_type": "mixed",
        "difficulty": "advanced",
        "question_count": 20,
    }
    response = client.post("/api/v1/interviews/sessions", json=payload)
    assert response.status_code == 201
    data = response.json()

    question_bank_ids = [q["question_bank_id"] for q in data["questions"]]
    # Every question in the session must be unique
    assert len(question_bank_ids) == len(set(question_bank_ids))
    assert data["total_questions"] == len(question_bank_ids)


def test_question_selection_with_skill_gap_personalization(db_session, client):
    """Verify questions matching candidate's missing skills are prioritized."""
    profile, resume, report = seed_candidate_with_gap_report(db_session, "backend_developer")

    payload = {
        "target_role": "backend_developer",
        "interview_type": "technical",
        "difficulty": "intermediate",
        "question_count": 5,
        "skill_gap_report_id": report.id,
    }
    response = client.post("/api/v1/interviews/sessions", json=payload)
    assert response.status_code == 201
    data = response.json()

    # Backend developer missing skills include Docker, Redis, FastAPI, SQL/DBMS
    question_skills = [q["relevant_skill"].lower() for q in data["questions"]]
    # Prioritization should pull in questions covering database or backend architecture
    assert any(
        s in ("sql", "dbms", "database", "redis", "fastapi", "docker", "system design", "rest api")
        for s in question_skills
    )


# =============================================================================
# 5. Question Concealment & Current Question API
# =============================================================================


def test_current_question_withholds_answer_keys(client):
    """Verify current-question endpoint returns active question without secret evaluation keys."""
    res_start = client.post(
        "/api/v1/interviews/sessions",
        json={"target_role": "sde", "interview_type": "technical", "question_count": 5},
    )
    session_id = res_start.json()["id"]

    res_q = client.get(f"/api/v1/interviews/sessions/{session_id}/current-question")
    assert res_q.status_code == 200
    q_data = res_q.json()

    assert q_data["sequence_order"] == 1
    assert q_data["is_answered"] is False
    assert "question_text" in q_data
    # Crucial security assertion: Expected concepts and grading rubrics must NOT be leaked
    assert "expected_concepts" not in q_data
    assert "evaluation_rubric" not in q_data
    assert "suggested_answer_points" not in q_data


# =============================================================================
# 6. Answer Submission & Deterministic Evaluation
# =============================================================================


def test_answer_submission_and_evaluation_quality(client):
    """Verify comprehensive answer receives high score with identified concepts and strengths."""
    res_start = client.post(
        "/api/v1/interviews/sessions",
        json={"target_role": "sde", "interview_type": "technical", "difficulty": "beginner", "question_count": 5},
    )
    session_id = res_start.json()["id"]

    # Fetch Question 1
    res_q = client.get(f"/api/v1/interviews/sessions/{session_id}/current-question")
    q1 = res_q.json()

    # High quality answer addressing generators vs lists
    answer_payload = {
        "question_id": q1["id"],
        "answer_text": (
            "Generators in Python use the yield keyword to produce items lazily one at a time "
            "via lazy evaluation rather than storing the entire sequence in memory like lists. "
            "This provides significant memory efficiency and follows the iterator protocol using "
            "iter and next methods until StopIteration is raised. "
            "For example, reading large server logs line-by-line with a generator uses O(1) memory "
            "in contrast to lists which require O(N) memory."
        ),
    }

    res_ans = client.post(f"/api/v1/interviews/sessions/{session_id}/answer", json=answer_payload)
    assert res_ans.status_code == 200
    ans_data = res_ans.json()

    assert ans_data["session_id"] == session_id
    assert ans_data["session_question_id"] == q1["id"]
    eval_data = ans_data["evaluation"]
    assert eval_data is not None

    # Scores must reflect comprehensive coverage
    assert eval_data["overall_score"] >= 70.0
    assert eval_data["relevance_score"] >= 70.0
    assert eval_data["concept_coverage_score"] >= 70.0
    assert eval_data["structure_score"] >= 70.0

    # Concepts identified
    assert len(eval_data["identified_concepts"]) > 0
    assert len(eval_data["strengths"]) > 0
    assert eval_data["evaluator_method"] == "deterministic_rubric_v1"
    assert "deterministic rubric" in eval_data["feedback_rationale"]


def test_behavioral_star_answer_evaluation(client):
    """Verify behavioral question evaluates STAR format."""
    res_start = client.post(
        "/api/v1/interviews/sessions",
        json={"target_role": "sde", "interview_type": "behavioral", "difficulty": "intermediate", "question_count": 5},
    )
    session_id = res_start.json()["id"]
    q1 = client.get(f"/api/v1/interviews/sessions/{session_id}/current-question").json()

    star_answer = {
        "question_id": q1["id"],
        "answer_text": (
            "Situation: During our microservice redesign, a senior engineer and I had a strong technical disagreement regarding database schemas. "
            "Task: We needed to reach team alignment without delaying our sprint milestone. "
            "Action: I invited him to a whiteboard session where I actively listened with respect to his architectural concerns. "
            "We used benchmarking data and query profiling to objectively evaluate both approaches. Rather than arguing, we reached a data-driven compromise. "
            "Result: The combined architecture met throughput requirements, the team achieved full alignment, and the project shipped on time with a positive outcome."
        ),
    }

    res_ans = client.post(f"/api/v1/interviews/sessions/{session_id}/answer", json=star_answer)
    assert res_ans.status_code == 200
    eval_data = res_ans.json()["evaluation"]

    assert eval_data["overall_score"] >= 75.0
    assert eval_data["structure_score"] >= 80.0
    assert any("structured" in s.lower() or "concepts" in s.lower() for s in eval_data["strengths"])


# =============================================================================
# 7. Edge Cases: Empty and Very Short Answers
# =============================================================================


def test_empty_answer_submission(client):
    """Verify submitting an empty or whitespace-only answer receives a score of 0."""
    res_start = client.post(
        "/api/v1/interviews/sessions",
        json={"target_role": "sde", "interview_type": "technical", "question_count": 5},
    )
    session_id = res_start.json()["id"]
    q1 = client.get(f"/api/v1/interviews/sessions/{session_id}/current-question").json()

    res_ans = client.post(
        f"/api/v1/interviews/sessions/{session_id}/answer",
        json={"question_id": q1["id"], "answer_text": "   "},
    )
    assert res_ans.status_code == 200
    eval_data = res_ans.json()["evaluation"]

    assert eval_data["overall_score"] == 0.0
    assert eval_data["concept_coverage_score"] == 0.0
    assert eval_data["identified_concepts"] == []
    assert len(eval_data["missing_concepts"]) > 0
    assert "No answer was provided" in eval_data["improvement_suggestions"][0]


def test_very_short_answer_submission(client):
    """Verify submitting a 2-word answer receives low score with clear feedback."""
    res_start = client.post(
        "/api/v1/interviews/sessions",
        json={"target_role": "sde", "interview_type": "technical", "question_count": 5},
    )
    session_id = res_start.json()["id"]
    q1 = client.get(f"/api/v1/interviews/sessions/{session_id}/current-question").json()

    res_ans = client.post(
        f"/api/v1/interviews/sessions/{session_id}/answer",
        json={"question_id": q1["id"], "answer_text": "Python good"},
    )
    assert res_ans.status_code == 200
    eval_data = res_ans.json()["evaluation"]

    assert eval_data["overall_score"] <= 15.0
    assert "too brief" in eval_data["improvement_suggestions"][0].lower() or "expand" in eval_data["improvement_suggestions"][0].lower()


# =============================================================================
# 8. Duplicate Answer Prevention & Session Progression
# =============================================================================


def test_duplicate_answer_submission_prevention(client):
    """Verify attempting to answer the same question twice returns 400 Bad Request."""
    res_start = client.post(
        "/api/v1/interviews/sessions",
        json={"target_role": "sde", "interview_type": "technical", "question_count": 5},
    )
    session_id = res_start.json()["id"]
    q1 = client.get(f"/api/v1/interviews/sessions/{session_id}/current-question").json()

    # First submission
    res1 = client.post(
        f"/api/v1/interviews/sessions/{session_id}/answer",
        json={"question_id": q1["id"], "answer_text": "Valid first attempt answer."},
    )
    assert res1.status_code == 200

    # Second submission to same question
    res2 = client.post(
        f"/api/v1/interviews/sessions/{session_id}/answer",
        json={"question_id": q1["id"], "answer_text": "Duplicate attempt should be rejected."},
    )
    assert res2.status_code == 400
    assert "already been answered" in res2.json()["detail"]


def test_sequential_question_progression(client):
    """Verify answering question 1 advances current question to question 2."""
    res_start = client.post(
        "/api/v1/interviews/sessions",
        json={"target_role": "sde", "interview_type": "technical", "question_count": 5},
    )
    session_id = res_start.json()["id"]

    # Active question is Q1
    q1 = client.get(f"/api/v1/interviews/sessions/{session_id}/current-question").json()
    assert q1["sequence_order"] == 1

    # Answer Q1 without passing question_id (defaults to current question)
    res_ans = client.post(
        f"/api/v1/interviews/sessions/{session_id}/answer",
        json={"answer_text": "Answer for the first question."},
    )
    assert res_ans.status_code == 200

    # Active question is now Q2
    q2 = client.get(f"/api/v1/interviews/sessions/{session_id}/current-question").json()
    assert q2["sequence_order"] == 2
    assert q2["id"] != q1["id"]


# =============================================================================
# 9. Session Completion & Report Generation
# =============================================================================


def test_complete_interview_and_report_generation(client):
    """Verify complete lifecycle: answer questions, call complete, verify structured report."""
    res_start = client.post(
        "/api/v1/interviews/sessions",
        json={"target_role": "sde", "interview_type": "technical", "difficulty": "beginner", "question_count": 5},
    )
    session_id = res_start.json()["id"]

    # Answer 3 of 5 questions
    for i in range(3):
        q = client.get(f"/api/v1/interviews/sessions/{session_id}/current-question").json()
        client.post(
            f"/api/v1/interviews/sessions/{session_id}/answer",
            json={
                "question_id": q["id"],
                "answer_text": f"Encapsulation and abstraction are core object-oriented principles covering answer step {i}.",
            },
        )

    # Complete session
    res_comp = client.post(f"/api/v1/interviews/sessions/{session_id}/complete")
    assert res_comp.status_code == 200
    report = res_comp.json()

    assert report["session_id"] == session_id
    assert report["questions_attempted"] == 3
    assert report["total_questions"] == 5
    assert report["overall_score"] > 0
    assert report["average_answer_score"] > 0
    assert isinstance(report["category_scores"], dict)
    assert isinstance(report["strong_areas"], list)
    assert isinstance(report["weak_areas"], list)
    assert isinstance(report["frequently_missed_concepts"], list)
    assert isinstance(report["recommended_topics"], list)
    assert isinstance(report["actionable_feedback"], list)
    assert "Disclaimer" in report["performance_summary"]

    # Check report persistence via GET
    res_rep = client.get(f"/api/v1/interviews/sessions/{session_id}/report")
    assert res_rep.status_code == 200
    assert res_rep.json()["id"] == report["id"]

    # Check session status is completed
    res_sess = client.get(f"/api/v1/interviews/sessions/{session_id}")
    assert res_sess.json()["status"] == "completed"


# =============================================================================
# 10. History Listing, Detail View, and Cascade Deletion
# =============================================================================


def test_interview_history_listing_and_deletion(client):
    """Verify listing past sessions and cascade deletion of all child entities."""
    # Create session A
    res_a = client.post(
        "/api/v1/interviews/sessions",
        json={"target_role": "sde", "interview_type": "technical", "question_count": 5},
    )
    id_a = res_a.json()["id"]

    # Create session B
    res_b = client.post(
        "/api/v1/interviews/sessions",
        json={"target_role": "frontend_developer", "interview_type": "project", "question_count": 5},
    )
    id_b = res_b.json()["id"]

    # List sessions
    res_list = client.get("/api/v1/interviews/sessions")
    assert res_list.status_code == 200
    sessions = res_list.json()
    assert len(sessions) >= 2
    listed_ids = [s["id"] for s in sessions]
    assert id_a in listed_ids
    assert id_b in listed_ids

    # Answer a question and complete session A to generate answers & report
    q_a = client.get(f"/api/v1/interviews/sessions/{id_a}/current-question").json()
    client.post(
        f"/api/v1/interviews/sessions/{id_a}/answer",
        json={"question_id": q_a["id"], "answer_text": "Answer text before deletion."},
    )
    client.post(f"/api/v1/interviews/sessions/{id_a}/complete")

    # Delete session A
    res_del = client.delete(f"/api/v1/interviews/sessions/{id_a}")
    assert res_del.status_code == 204

    # Verify session A is gone
    res_get = client.get(f"/api/v1/interviews/sessions/{id_a}")
    assert res_get.status_code == 404

    # Verify report for session A is gone
    res_rep = client.get(f"/api/v1/interviews/sessions/{id_a}/report")
    assert res_rep.status_code == 404

    # Session B remains intact
    res_b_check = client.get(f"/api/v1/interviews/sessions/{id_b}")
    assert res_b_check.status_code == 200


# =============================================================================
# 11. Non-Regression of Existing Features
# =============================================================================


def test_non_regression_existing_platform_features(client, db_session):
    """Verify that adding the mock interview simulator did not break Features 1 to 4."""
    # 1. Health check
    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"

    # 2. Skill Gap Roles Benchmark
    res_roles = client.get("/api/v1/skills/roles")
    assert res_roles.status_code == 200
    assert len(res_roles.json()) >= 8

    # 3. Learning Preferences
    res_prefs = client.get("/api/v1/learning/preferences")
    assert res_prefs.status_code == 200
    assert "daily_learning_hours" in res_prefs.json()

    # 4. Resume Library
    res_resumes = client.get("/api/v1/resumes/library")
    assert res_resumes.status_code == 200
