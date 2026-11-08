"""
Unit tests for CareerMind AI database architecture, constraints, and cascade behaviors.
"""

import uuid
import pytest
from sqlalchemy import create_engine, select, text, exc, event
from sqlalchemy.orm import sessionmaker

from database.base import Base
from database.models import (
    CareerProfile,
    CareerGoal,
    LearningPreference,
    ResumeRecord,
    ResumeProfile,
    ResumeSkill,
    ResumeEducation,
    ResumeExperience,
    ResumeProject,
    ResumeCertification,
)
from services.career_profile_service import (
    create_or_update_local_career_profile,
    get_local_career_profile,
    set_career_goals,
    set_learning_preferences,
)
from services.resume_library_service import (
    register_uploaded_resume,
    set_default_resume,
    delete_resume_record,
    get_resume_records,
)
from schemas.career_profile_schema import CareerProfileCreate
from schemas.career_goal_schema import CareerGoalCreate
from schemas.learning_preference_schema import LearningPreferenceCreate


@pytest.fixture
def db_session():
    """Create an isolated, in-memory SQLite test database with foreign keys enabled."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        echo=False,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = TestingSession()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


# =============================================================================
# 1. CareerProfile & Single Local Profile Enforcement
# =============================================================================

def test_career_profile_crud_and_single_local_user_enforcement(db_session):
    """Verify CareerProfile creation and strict single-user unique constraint."""
    profile_in = CareerProfileCreate(
        full_name="Alex Reed",
        career_status="Experienced",
        highest_education="Bachelor's",
        degree="B.S. Computer Science",
        institution="UC Berkeley",
        graduation_year=2022,
        primary_target_role="Senior Backend Developer",
        preferred_job_type="Full-time",
        preferred_work_mode="Remote",
        preferred_locations=["San Francisco", "New York"],
        career_objective="Build high-throughput distributed microservices.",
    )

    # 1. Create profile
    profile = create_or_update_local_career_profile(db_session, profile_in)
    assert profile.id is not None
    assert profile.user_id == "local_user"
    assert profile.onboarding_completed is True
    assert profile.full_name == "Alex Reed"

    # 2. Retrieve profile
    fetched = get_local_career_profile(db_session)
    assert fetched is not None
    assert fetched.id == profile.id

    # 3. Prevent duplicate local user (Unique constraint on user_id)
    with pytest.raises(exc.IntegrityError):
        duplicate_profile = CareerProfile(
            user_id="local_user",  # Duplicate user_id
            full_name="Impostor User",
            career_status="Fresher",
            highest_education="High School",
            degree="None",
            institution="Unknown",
            graduation_year=2025,
            primary_target_role="Intern",
            preferred_job_type="Part-time",
            preferred_work_mode="On-site",
            preferred_locations=[],
        )
        db_session.add(duplicate_profile)
        db_session.commit()
    db_session.rollback()


def test_career_goals_and_learning_preferences(db_session):
    """Verify 1-to-1 CareerGoals and LearningPreferences relationships."""
    profile_in = CareerProfileCreate(
        full_name="Jordan Lee",
        career_status="Fresher",
        highest_education="Master's",
        degree="M.S. Data Science",
        institution="MIT",
        graduation_year=2024,
        primary_target_role="Data Scientist",
        preferred_job_type="Full-time",
        preferred_work_mode="Hybrid",
        preferred_locations=["Boston"],
    )
    profile = create_or_update_local_career_profile(db_session, profile_in)

    # Add CareerGoals
    goals_in = CareerGoalCreate(
        target_roles=["Data Scientist", "ML Engineer"],
        preferred_locations=["Boston", "Remote"],
        preferred_work_modes=["Hybrid", "Remote"],
        preferred_job_types=["Full-time"],
        expected_salary="$120,000 - $140,000",
        job_search_timeline="Immediately",
    )
    goals = set_career_goals(db_session, profile.id, goals_in)
    assert goals.career_profile_id == profile.id
    assert "Data Scientist" in goals.target_roles

    # Add LearningPreferences
    prefs_in = LearningPreferenceCreate(
        learning_objective="Master PyTorch and Transformers",
        daily_learning_hours=2.5,
        preferred_language="Python",
        interview_preparation_type="Coding & Machine Learning",
        preferred_learning_style="Hands-on projects",
    )
    prefs = set_learning_preferences(db_session, profile.id, prefs_in)
    assert prefs.career_profile_id == profile.id
    assert prefs.daily_learning_hours == 2.5


# =============================================================================
# 2. Resume Library & Default Resume Integrity
# =============================================================================

def test_resume_library_default_management_and_uniqueness(db_session):
    """Verify atomic default resume assignment and partial unique index."""
    profile_in = CareerProfileCreate(
        full_name="Morgan Chen",
        career_status="Experienced",
        highest_education="Bachelor's",
        degree="B.Eng Software",
        institution="UCLA",
        graduation_year=2020,
        primary_target_role="Full Stack Engineer",
        preferred_job_type="Full-time",
        preferred_work_mode="Remote",
        preferred_locations=["Seattle"],
    )
    profile = create_or_update_local_career_profile(db_session, profile_in)

    file_id_1 = "11111111111111111111111111111111"
    file_id_2 = "22222222222222222222222222222222"
    file_id_3 = "33333333333333333333333333333333"

    # 1. First resume automatically becomes default
    res1 = register_uploaded_resume(
        db_session,
        career_profile_id=profile.id,
        file_id=file_id_1,
        original_filename="morgan_sde.pdf",
        file_size=204800,
        display_name="SDE Resume",
    )
    assert res1.is_default is True
    assert "data/uploads" in res1.file_path.replace("\\", "/")

    # 2. Second resume is not default
    res2 = register_uploaded_resume(
        db_session,
        career_profile_id=profile.id,
        file_id=file_id_2,
        original_filename="morgan_frontend.pdf",
        file_size=180000,
        display_name="Frontend Resume",
    )
    assert res2.is_default is False

    # 3. Third resume is not default
    res3 = register_uploaded_resume(
        db_session,
        career_profile_id=profile.id,
        file_id=file_id_3,
        original_filename="morgan_lead.pdf",
        file_size=250000,
        display_name="Tech Lead Resume",
    )
    assert res3.is_default is False

    # 4. Partial unique index prevents duplicate defaults at the database level
    with pytest.raises(exc.IntegrityError):
        db_session.execute(
            text("UPDATE resume_records SET is_default = 1 WHERE id = :rid"),
            {"rid": res2.id},
        )
        db_session.commit()
    db_session.rollback()

    # 5. Service layer safely switches default
    set_default_resume(db_session, profile.id, res2.id)
    db_session.refresh(res1)
    db_session.refresh(res2)
    assert res1.is_default is False
    assert res2.is_default is True

    # 6. Deleting default automatically promotes next remaining resume
    delete_resume_record(db_session, profile.id, res2.id)
    records = get_resume_records(db_session, profile.id)
    assert len(records) == 2
    # Exactly one resume is default
    defaults = [r for r in records if r.is_default]
    assert len(defaults) == 1

    # 7. Delete all resumes -> 0 resumes left, clean state
    for r in list(records):
        delete_resume_record(db_session, profile.id, r.id)
    remaining = get_resume_records(db_session, profile.id)
    assert len(remaining) == 0


def test_duplicate_file_id_rejected(db_session):
    """Verify that file_id must be unique across all records."""
    profile_in = CareerProfileCreate(
        full_name="Taylor Swift",
        career_status="Experienced",
        highest_education="None",
        degree="Music",
        institution="Nashville",
        graduation_year=2008,
        primary_target_role="Artist",
        preferred_job_type="Contract",
        preferred_work_mode="Remote",
        preferred_locations=[],
    )
    profile = create_or_update_local_career_profile(db_session, profile_in)

    file_id = "44444444444444444444444444444444"
    register_uploaded_resume(
        db_session,
        career_profile_id=profile.id,
        file_id=file_id,
        original_filename="resume_v1.pdf",
        file_size=1000,
    )

    with pytest.raises(ValueError, match="already registered"):
        register_uploaded_resume(
            db_session,
            career_profile_id=profile.id,
            file_id=file_id,
            original_filename="resume_v2.pdf",
            file_size=2000,
        )


# =============================================================================
# 3. Resume-Specific Data Isolation & Cascade Deletions
# =============================================================================

def test_resume_specific_data_isolation(db_session):
    """
    Verify that Resume A and Resume B maintain completely independent parsed data.
    Deleting Resume A leaves Resume B completely intact.
    """
    profile = create_or_update_local_career_profile(
        db_session,
        CareerProfileCreate(
            full_name="Casey Rivera",
            career_status="Experienced",
            highest_education="Bachelor's",
            degree="Computer Science",
            institution="UW",
            graduation_year=2021,
            primary_target_role="Software Engineer",
            preferred_job_type="Full-time",
            preferred_work_mode="Hybrid",
            preferred_locations=["Seattle"],
        ),
    )

    # Resume A: Backend Resume
    res_a = register_uploaded_resume(
        db_session,
        career_profile_id=profile.id,
        file_id="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        original_filename="casey_backend.pdf",
        file_size=150000,
    )
    rp_a = ResumeProfile(
        resume_record_id=res_a.id,
        full_name="Casey Rivera",
        email="casey.backend@example.com",
    )
    db_session.add(rp_a)
    db_session.flush()

    db_session.add(ResumeSkill(resume_profile_id=rp_a.id, skill_name="Python", category="programming_languages"))
    db_session.add(ResumeSkill(resume_profile_id=rp_a.id, skill_name="FastAPI", category="backend"))
    db_session.add(ResumeSkill(resume_profile_id=rp_a.id, skill_name="PostgreSQL", category="databases"))

    # Resume B: Data Analyst Resume
    res_b = register_uploaded_resume(
        db_session,
        career_profile_id=profile.id,
        file_id="bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        original_filename="casey_analyst.pdf",
        file_size=160000,
    )
    rp_b = ResumeProfile(
        resume_record_id=res_b.id,
        full_name="Casey Rivera",
        email="casey.data@example.com",
    )
    db_session.add(rp_b)
    db_session.flush()

    db_session.add(ResumeSkill(resume_profile_id=rp_b.id, skill_name="R", category="programming_languages"))
    db_session.add(ResumeSkill(resume_profile_id=rp_b.id, skill_name="Tableau", category="data_analytics"))
    db_session.add(ResumeSkill(resume_profile_id=rp_b.id, skill_name="Snowflake", category="databases"))
    db_session.commit()

    # Verify initial skills
    skills_a = db_session.execute(select(ResumeSkill).where(ResumeSkill.resume_profile_id == rp_a.id)).scalars().all()
    skills_b = db_session.execute(select(ResumeSkill).where(ResumeSkill.resume_profile_id == rp_b.id)).scalars().all()
    assert {s.skill_name for s in skills_a} == {"Python", "FastAPI", "PostgreSQL"}
    assert {s.skill_name for s in skills_b} == {"R", "Tableau", "Snowflake"}

    # Delete Resume A -> Resume B must remain completely untouched
    delete_resume_record(db_session, profile.id, res_a.id)

    # Resume A parsed profile and skills are gone
    assert db_session.get(ResumeProfile, rp_a.id) is None
    skills_a_after = db_session.execute(select(ResumeSkill).where(ResumeSkill.resume_profile_id == rp_a.id)).scalars().all()
    assert len(skills_a_after) == 0

    # Resume B parsed profile and skills remain completely intact
    assert db_session.get(ResumeProfile, rp_b.id) is not None
    skills_b_after = db_session.execute(select(ResumeSkill).where(ResumeSkill.resume_profile_id == rp_b.id)).scalars().all()
    assert {s.skill_name for s in skills_b_after} == {"R", "Tableau", "Snowflake"}


def test_career_profile_cascade_deletion(db_session):
    """Verify that deleting CareerProfile cascades and deletes all associated records."""
    profile = create_or_update_local_career_profile(
        db_session,
        CareerProfileCreate(
            full_name="Sam Altman",
            career_status="Experienced",
            highest_education="Dropped Out",
            degree="CS",
            institution="Stanford",
            graduation_year=2005,
            primary_target_role="CEO",
            preferred_job_type="Full-time",
            preferred_work_mode="On-site",
            preferred_locations=["San Francisco"],
        ),
    )

    res = register_uploaded_resume(
        db_session,
        career_profile_id=profile.id,
        file_id="cccccccccccccccccccccccccccccccc",
        original_filename="sam.pdf",
        file_size=100000,
    )
    rp = ResumeProfile(resume_record_id=res.id, full_name="Sam Altman")
    db_session.add(rp)
    db_session.flush()
    db_session.add(ResumeSkill(resume_profile_id=rp.id, skill_name="Strategy", category="other"))
    db_session.commit()

    # Delete CareerProfile
    db_session.delete(profile)
    db_session.commit()

    # All children cascaded
    assert db_session.get(ResumeRecord, res.id) is None
    assert db_session.get(ResumeProfile, rp.id) is None
    skills = db_session.execute(select(ResumeSkill).where(ResumeSkill.resume_profile_id == rp.id)).scalars().all()
    assert len(skills) == 0

