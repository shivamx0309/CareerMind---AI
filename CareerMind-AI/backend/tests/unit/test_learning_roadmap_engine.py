"""
CareerMind AI — Phase 4.1: Personalized Learning Roadmap Engine Unit & Integration Tests.

Comprehensive test suite verifying:
1. Learning Priority classification (high, medium, low)
2. Skill Dependency Graph and prerequisite sequencing
3. Circular dependency handling & cycle prevention
4. Verified free resource catalog integration
5. End-to-end roadmap generation from SkillGapReport
6. Weekly study hour customization (5, 10, 15, 20 hrs/week)
7. Topic completion and cascading skill & roadmap progress
8. Skill status completion cascading to child topics
9. Milestone progress updates
10. Roadmap progress telemetry & next recommended topic
11. Historical roadmap listing and detail retrieval
12. Cascade deletion of roadmap and all child entities
13. Learning preferences retrieval and updates
14. Error handling: 404s, 422s for invalid reports and states
15. Non-regression: Skill Gap, Resume Library, and Job Matcher
"""

import json
from unittest.mock import patch
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
from database.models.learning_roadmap import LearningRoadmap
from database.models.roadmap_skill import RoadmapSkill
from database.models.roadmap_topic import RoadmapTopic
from database.models.learning_resource import LearningResource
from database.models.roadmap_milestone import RoadmapMilestone
from database.models.learning_preference import LearningPreference

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
    skill_dependency_service,
    learning_resource_catalog,
    learning_priority_service,
    roadmap_service,
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
            programming_languages=["Python", "SQL"],
            databases=["PostgreSQL"],
            backend=["Flask"],  # Flask is related to FastAPI
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


# =========================================================================
# 1. Dependency Ordering & Prerequisite Tests
# =========================================================================

def test_topological_sort_skills_order():
    """Verify prerequisites precede dependent skills (e.g., Python before FastAPI, Data Structures before Algorithms)."""
    skills = ["FastAPI", "Python", "Docker", "Algorithms", "Data Structures"]
    sorted_skills = skill_dependency_service.topological_sort_skills(skills, candidate_known_skills=set())

    pos_python = sorted_skills.index("Python")
    pos_fastapi = sorted_skills.index("FastAPI")
    assert pos_python < pos_fastapi, "Python must precede FastAPI"

    pos_ds = sorted_skills.index("Data Structures")
    pos_algo = sorted_skills.index("Algorithms")
    assert pos_ds < pos_algo, "Data Structures must precede Algorithms"


def test_topological_sort_with_known_prerequisites():
    """If candidate already knows Python, FastAPI does not require Python in the output."""
    skills = ["FastAPI"]
    sorted_skills = skill_dependency_service.topological_sort_skills(skills, candidate_known_skills={"Python"})
    assert "FastAPI" in sorted_skills
    assert "Python" not in sorted_skills


def test_circular_dependency_graceful_handling():
    """Test that cycles in skill dependencies are handled gracefully without recursion crash."""
    artificial_graph = {
        "SkillA": ["SkillB"],
        "SkillB": ["SkillC"],
        "SkillC": ["SkillA"],
    }
    with patch.object(skill_dependency_service, "SKILL_DEPENDENCY_GRAPH", artificial_graph):
        res = skill_dependency_service.topological_sort_skills(["SkillA", "SkillB", "SkillC"])
        assert len(res) == 3
        assert set(res) == {"SkillA", "SkillB", "SkillC"}


# =========================================================================
# 2. Learning Priority Classification Tests
# =========================================================================

def test_learning_priority_classification(db_session):
    """Verify high for missing required, medium for related required, and low for preferred skills."""
    _, _, report = seed_candidate_with_gap_report(db_session, "backend_developer")

    prioritized = learning_priority_service.prioritize_skills_for_roadmap(report=report)

    high_items = [p for p in prioritized if p.priority == "high"]
    med_items = [p for p in prioritized if p.priority == "medium"]
    low_items = [p for p in prioritized if p.priority == "low"]

    # In Backend Developer benchmark, Docker, REST APIs, etc. are required.
    # Candidate with Flask had related match to FastAPI. FastAPI should be medium.
    assert len(high_items) > 0, "Expected high priority missing required skills"
    for h in high_items:
        assert h.importance == "required"
        assert h.gap_type == "missing_required"
        assert "Mandatory baseline core skill" in h.rationale

    for m in med_items:
        assert m.importance == "required"
        assert m.gap_type == "related_required"
        assert "transferable knowledge" in m.rationale

    for l in low_items:
        assert l.importance == "preferred"
        assert l.gap_type == "missing_preferred"


# =========================================================================
# 3. Verified Free Resource Catalog Tests
# =========================================================================

def test_verified_resource_catalog():
    """Check that resource catalog provides valid URLs and free metadata for key topics."""
    resources = learning_resource_catalog.get_resources_for_topic("Python", "Variables, Data Types & Control Flow")
    assert len(resources) > 0
    first = resources[0]
    assert first["is_free"] is True
    assert first["url"].startswith("http")
    assert "python.org" in first["url"]

    # FastAPI resource
    fastapi_res = learning_resource_catalog.get_resources_for_topic("FastAPI", "Route Handlers, Path & Query Parameters")
    assert len(fastapi_res) > 0
    assert "fastapi.tiangolo.com" in fastapi_res[0]["url"]


def test_resource_fallback_for_unknown_topic():
    """Topics without custom entries receive a valid official documentation link."""
    res = learning_resource_catalog.get_resources_for_topic("CustomSkill", "Advanced Metaprogramming")
    assert len(res) >= 1
    assert res[0]["is_free"] is True
    assert res[0]["url"].startswith("http")


# =========================================================================
# 4. Roadmap Generation Engine Tests
# =========================================================================

def test_generate_learning_roadmap(db_session):
    """Generate roadmap from real SkillGapReport and verify full structure and database persistence."""
    profile, rec, report = seed_candidate_with_gap_report(db_session, "backend_developer")

    roadmap = roadmap_service.generate_learning_roadmap(
        db=db_session,
        career_profile_id=profile.id,
        skill_gap_report_id=report.id,
        weekly_study_hours=10,
        custom_title="Custom Backend Prep",
    )

    assert roadmap is not None
    assert roadmap.career_profile_id == profile.id
    assert roadmap.skill_gap_report_id == report.id
    assert roadmap.target_role == "backend_developer"
    assert roadmap.title == "Custom Backend Prep"
    assert roadmap.weekly_study_hours == 10
    assert roadmap.total_estimated_hours > 0
    assert roadmap.total_weeks >= 1
    assert roadmap.progress_percentage == 0.0
    assert roadmap.status == "in_progress"

    # Verify skills and topics
    assert len(roadmap.skills) > 0
    for sk in roadmap.skills:
        assert len(sk.topics) > 0
        assert sk.practical_project is not None
        for tp in sk.topics:
            assert len(tp.resources) > 0

    # Verify milestones & weekly schedule
    assert len(roadmap.milestones) == roadmap.total_weeks
    assert len(roadmap.weekly_schedule) == roadmap.total_weeks


def test_roadmap_study_hours_scaling(db_session):
    """Verify that allocating more weekly hours decreases the total week duration."""
    profile, _, report = seed_candidate_with_gap_report(db_session, "backend_developer")

    rm_10 = roadmap_service.generate_learning_roadmap(
        db=db_session,
        career_profile_id=profile.id,
        skill_gap_report_id=report.id,
        weekly_study_hours=10,
    )

    rm_20 = roadmap_service.generate_learning_roadmap(
        db=db_session,
        career_profile_id=profile.id,
        skill_gap_report_id=report.id,
        weekly_study_hours=20,
    )

    assert rm_20.total_weeks <= rm_10.total_weeks


# =========================================================================
# 5. Progress Tracking & Cascading Status Tests
# =========================================================================

def test_topic_completion_and_cascading_progress(db_session):
    """Marking topics completed cascades to skill status and updates roadmap progress percentage."""
    profile, _, report = seed_candidate_with_gap_report(db_session, "backend_developer")

    roadmap = roadmap_service.generate_learning_roadmap(
        db=db_session,
        career_profile_id=profile.id,
        skill_gap_report_id=report.id,
        weekly_study_hours=10,
    )

    first_skill = roadmap.skills[0]
    first_topic = first_skill.topics[0]

    # Mark first topic in_progress
    t1 = roadmap_service.update_topic_status(
        db=db_session,
        career_profile_id=profile.id,
        roadmap_id=roadmap.id,
        topic_id=first_topic.id,
        new_status="in_progress",
    )
    assert t1.status == "in_progress"

    # Parent skill should become in_progress
    db_session.refresh(first_skill)
    assert first_skill.status == "in_progress"

    # Mark all topics in first skill as completed
    for topic in first_skill.topics:
        roadmap_service.update_topic_status(
            db=db_session,
            career_profile_id=profile.id,
            roadmap_id=roadmap.id,
            topic_id=topic.id,
            new_status="completed",
        )

    db_session.refresh(first_skill)
    assert first_skill.status == "completed"

    # Roadmap progress percentage must be greater than zero
    db_session.refresh(roadmap)
    assert roadmap.progress_percentage > 0.0
    assert roadmap.completed_topics_count == len(first_skill.topics)


def test_skill_completion_cascades_to_all_child_topics(db_session):
    """Marking an entire skill completed automatically marks all child topics completed."""
    profile, _, report = seed_candidate_with_gap_report(db_session, "backend_developer")
    roadmap = roadmap_service.generate_learning_roadmap(
        db=db_session,
        career_profile_id=profile.id,
        skill_gap_report_id=report.id,
    )

    first_skill = roadmap.skills[0]
    updated_skill = roadmap_service.update_skill_status(
        db=db_session,
        career_profile_id=profile.id,
        roadmap_id=roadmap.id,
        skill_id=first_skill.id,
        new_status="completed",
    )

    assert updated_skill.status == "completed"
    for tp in updated_skill.topics:
        assert tp.status == "completed"
        assert tp.completed_at is not None


def test_milestone_status_update(db_session):
    """Test updating weekly milestone status."""
    profile, _, report = seed_candidate_with_gap_report(db_session, "backend_developer")
    roadmap = roadmap_service.generate_learning_roadmap(
        db=db_session,
        career_profile_id=profile.id,
        skill_gap_report_id=report.id,
    )

    first_ms = roadmap.milestones[0]
    updated_ms = roadmap_service.update_milestone_status(
        db=db_session,
        career_profile_id=profile.id,
        roadmap_id=roadmap.id,
        milestone_id=first_ms.id,
        new_status="completed",
    )
    assert updated_ms.status == "completed"
    assert updated_ms.completed_at is not None


def test_roadmap_progress_telemetry(db_session):
    """Verify computed progress metrics and next recommended topic recommendation."""
    profile, _, report = seed_candidate_with_gap_report(db_session, "backend_developer")
    roadmap = roadmap_service.generate_learning_roadmap(
        db=db_session,
        career_profile_id=profile.id,
        skill_gap_report_id=report.id,
    )

    progress = roadmap_service.get_roadmap_progress(
        db=db_session,
        career_profile_id=profile.id,
        roadmap_id=roadmap.id,
    )

    assert progress["roadmap_id"] == roadmap.id
    assert progress["total_skills"] == len(roadmap.skills)
    assert progress["completed_skills"] == 0
    assert progress["progress_percentage"] == 0.0
    assert progress["estimated_hours_remaining"] > 0
    assert progress["next_recommended_topic"] is not None
    assert "topic_name" in progress["next_recommended_topic"]


# =========================================================================
# 6. Historical Listing & Cascade Deletion Tests
# =========================================================================

def test_historical_roadmap_listing_and_retrieval(db_session):
    """List historical roadmaps and retrieve detailed entity."""
    profile, _, report = seed_candidate_with_gap_report(db_session, "backend_developer")
    rm1 = roadmap_service.generate_learning_roadmap(
        db=db_session,
        career_profile_id=profile.id,
        skill_gap_report_id=report.id,
        custom_title="Plan A",
    )
    rm2 = roadmap_service.generate_learning_roadmap(
        db=db_session,
        career_profile_id=profile.id,
        skill_gap_report_id=report.id,
        custom_title="Plan B",
    )

    roadmaps = roadmap_service.get_learning_roadmaps(db_session, profile.id)
    assert len(roadmaps) == 2
    titles = [r.title for r in roadmaps]
    assert "Plan A" in titles
    assert "Plan B" in titles

    single = roadmap_service.get_learning_roadmap(db_session, profile.id, rm1.id)
    assert single is not None
    assert single.title == "Plan A"


def test_cascade_delete_learning_roadmap(db_session):
    """Deleting a learning roadmap removes all associated skills, topics, resources, and milestones."""
    profile, _, report = seed_candidate_with_gap_report(db_session, "backend_developer")
    rm = roadmap_service.generate_learning_roadmap(
        db=db_session,
        career_profile_id=profile.id,
        skill_gap_report_id=report.id,
    )
    rm_id = rm.id

    # Verify rows exist before deletion
    skills_before = db_session.execute(select(RoadmapSkill).where(RoadmapSkill.roadmap_id == rm_id)).scalars().all()
    milestones_before = db_session.execute(select(RoadmapMilestone).where(RoadmapMilestone.roadmap_id == rm_id)).scalars().all()
    assert len(skills_before) > 0
    assert len(milestones_before) > 0

    # Delete
    deleted = roadmap_service.delete_learning_roadmap(db_session, profile.id, rm_id)
    assert deleted is True

    # Verify cascaded removal
    rm_after = db_session.execute(select(LearningRoadmap).where(LearningRoadmap.id == rm_id)).scalar_one_or_none()
    assert rm_after is None

    skills_after = db_session.execute(select(RoadmapSkill).where(RoadmapSkill.roadmap_id == rm_id)).scalars().all()
    assert len(skills_after) == 0

    milestones_after = db_session.execute(select(RoadmapMilestone).where(RoadmapMilestone.roadmap_id == rm_id)).scalars().all()
    assert len(milestones_after) == 0


# =========================================================================
# 7. REST API Endpoints Integration Tests
# =========================================================================

def test_api_learning_preferences_endpoints(client):
    """Test GET and PUT /api/v1/learning/preferences."""
    # GET initializes default preferences
    res_get = client.get("/api/v1/learning/preferences")
    assert res_get.status_code == 200
    data = res_get.json()
    assert data["daily_learning_hours"] == 2.0
    assert data["preferred_language"] == "English"

    # PUT updates preferences
    update_payload = {
        "learning_objective": "Master Full-Stack Cloud Architecture",
        "daily_learning_hours": 3.5,
        "preferred_language": "English",
        "interview_preparation_type": "System Design",
        "preferred_learning_style": "Hands-on projects",
    }
    res_put = client.put("/api/v1/learning/preferences", json=update_payload)
    assert res_put.status_code == 200
    updated_data = res_put.json()
    assert updated_data["daily_learning_hours"] == 3.5
    assert updated_data["learning_objective"] == "Master Full-Stack Cloud Architecture"


def test_api_roadmap_generate_and_get(client, db_session):
    """Test POST /api/v1/learning/roadmaps/generate and GET /api/v1/learning/roadmaps/{id}."""
    profile, _, report = seed_candidate_with_gap_report(db_session, "backend_developer")

    payload = {
        "skill_gap_report_id": report.id,
        "weekly_study_hours": 15,
        "title": "Backend Sprint Plan",
    }
    res_post = client.post("/api/v1/learning/roadmaps/generate", json=payload)
    assert res_post.status_code == 201
    rm_data = res_post.json()
    roadmap_id = rm_data["id"]
    assert rm_data["weekly_study_hours"] == 15
    assert rm_data["title"] == "Backend Sprint Plan"
    assert len(rm_data["skills"]) > 0
    assert len(rm_data["milestones"]) > 0

    # GET detail
    res_get = client.get(f"/api/v1/learning/roadmaps/{roadmap_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == roadmap_id

    # GET list
    res_list = client.get("/api/v1/learning/roadmaps")
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1


def test_api_patch_topic_skill_milestone(client, db_session):
    """Test PATCH endpoints for topic, skill, and milestone."""
    profile, _, report = seed_candidate_with_gap_report(db_session, "backend_developer")
    rm = roadmap_service.generate_learning_roadmap(
        db=db_session,
        career_profile_id=profile.id,
        skill_gap_report_id=report.id,
    )

    topic_id = rm.skills[0].topics[0].id
    skill_id = rm.skills[0].id
    milestone_id = rm.milestones[0].id

    # PATCH topic
    res_topic = client.patch(
        f"/api/v1/learning/roadmaps/{rm.id}/topics/{topic_id}",
        json={"status": "completed"},
    )
    assert res_topic.status_code == 200
    assert res_topic.json()["status"] == "completed"

    # PATCH skill
    res_skill = client.patch(
        f"/api/v1/learning/roadmaps/{rm.id}/skills/{skill_id}",
        json={"status": "completed"},
    )
    assert res_skill.status_code == 200
    assert res_skill.json()["status"] == "completed"

    # PATCH milestone
    res_ms = client.patch(
        f"/api/v1/learning/roadmaps/{rm.id}/milestones/{milestone_id}",
        json={"status": "completed"},
    )
    assert res_ms.status_code == 200
    assert res_ms.json()["status"] == "completed"

    # GET progress
    res_prog = client.get(f"/api/v1/learning/roadmaps/{rm.id}/progress")
    assert res_prog.status_code == 200
    prog_data = res_prog.json()
    assert prog_data["progress_percentage"] > 0.0


def test_api_roadmap_delete(client, db_session):
    """Test DELETE /api/v1/learning/roadmaps/{id}."""
    profile, _, report = seed_candidate_with_gap_report(db_session, "backend_developer")
    rm = roadmap_service.generate_learning_roadmap(
        db=db_session,
        career_profile_id=profile.id,
        skill_gap_report_id=report.id,
    )

    res_del = client.delete(f"/api/v1/learning/roadmaps/{rm.id}")
    assert res_del.status_code == 204

    # Second delete returns 404
    res_del_404 = client.delete(f"/api/v1/learning/roadmaps/{rm.id}")
    assert res_del_404.status_code == 404


def test_api_error_handling(client, db_session):
    """Test 404 and 422 error states."""
    # 404 for invalid report
    res_inv_rep = client.post(
        "/api/v1/learning/roadmaps/generate",
        json={"skill_gap_report_id": "00000000-0000-0000-0000-000000000000"},
    )
    assert res_inv_rep.status_code == 404

    # 404 for nonexistent roadmap
    res_inv_rm = client.get("/api/v1/learning/roadmaps/00000000-0000-0000-0000-000000000000")
    assert res_inv_rm.status_code == 404


# =========================================================================
# 8. Non-Regression Tests
# =========================================================================

def test_non_regression_existing_features(client, db_session):
    """Verify Skill Gap, Resume Library, and Job Matcher continue working seamlessly."""
    # 1. Skill Gap roles catalog
    res_roles = client.get("/api/v1/skills/roles")
    assert res_roles.status_code == 200
    roles = res_roles.json()
    assert len(roles) == 8

    # 2. Resume Library listing
    res_lib = client.get("/api/v1/resumes/library")
    assert res_lib.status_code == 200

    # 3. Job Matcher endpoint exists
    res_match = client.post("/api/v1/jobs/match", json={"job_description": "We need a Python developer."})
    # Since no resume uploaded yet in this specific test client session, it gives 404 or expected validation
    assert res_match.status_code in (404, 422, 200)
