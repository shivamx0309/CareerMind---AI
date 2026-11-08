"""
CandidateProfile Two-Way Round-Trip Data Fidelity Test.
Verifies that persisting a CandidateProfile to relational tables and reconstructing it
preserves 100% data fidelity, types, and the existing Pydantic response contract.
"""

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from database.base import Base
from database.models import CareerProfile
from services.career_profile_service import create_or_update_local_career_profile
from services.resume_library_service import (
    register_uploaded_resume,
    persist_parsed_candidate_profile,
    reconstitute_candidate_profile,
)
from schemas.career_profile_schema import CareerProfileCreate
from schemas.candidate_schema import (
    CandidateProfile,
    PersonalInformation,
    TechnicalSkills,
    EducationEntry,
    ExperienceEntry,
    ProjectEntry,
    CertificationEntry,
    AchievementEntry,
)


@pytest.fixture
def db_session():
    """Create an isolated, in-memory SQLite database."""
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


def test_candidate_profile_comprehensive_roundtrip_fidelity(db_session):
    """
    Test complete round-trip preservation across all CandidateProfile components:
    - Personal Information
    - Professional Summary
    - All 10 TechnicalSkills categories
    - Multiple Education entries
    - Multiple Experience entries (with technologies list)
    - Multiple Project entries (with technologies list and project_url)
    - Multiple Certification entries
    - Multiple Achievement entries
    """
    # 1. Setup local profile and resume record
    profile = create_or_update_local_career_profile(
        db_session,
        CareerProfileCreate(
            full_name="Alex Reed",
            career_status="Experienced",
            highest_education="Bachelor's",
            degree="Computer Science",
            institution="UC Berkeley",
            graduation_year=2022,
            primary_target_role="Senior Backend Engineer",
            preferred_job_type="Full-time",
            preferred_work_mode="Remote",
            preferred_locations=["San Francisco"],
        ),
    )

    resume = register_uploaded_resume(
        db_session,
        career_profile_id=profile.id,
        file_id="1234567890abcdef1234567890abcdef",
        original_filename="alex_reed_master.pdf",
        file_size=204800,
        display_name="Master Resume",
    )

    # 2. Build rich CandidateProfile with all 10 categories and nested objects
    original = CandidateProfile(
        personal_information=PersonalInformation(
            full_name="Alex Reed",
            email="alex.reed@example.com",
            phone="+1 (555) 019-2834",
            linkedin="https://linkedin.com/in/alex-reed",
            github="https://github.com/alexreed-dev",
            portfolio="https://alexreed.dev",
            location="San Francisco, CA",
        ),
        professional_summary=(
            "Senior Software Engineer specializing in Python, distributed backend microservices, "
            "and scalable databases. Proven experience architecting asynchronous task queues."
        ),
        technical_skills=TechnicalSkills(
            programming_languages=["Python", "SQL", "Go", "TypeScript"],
            frontend=["React", "Tailwind CSS", "Next.js"],
            backend=["FastAPI", "Django", "Node.js", "Celery"],
            databases=["PostgreSQL", "Redis", "MongoDB", "ClickHouse"],
            data_analytics=["Pandas", "NumPy", "Apache Spark"],
            machine_learning=["Scikit-learn", "XGBoost"],
            deep_learning=["PyTorch", "Hugging Face"],
            cloud_devops=["Docker", "Kubernetes", "AWS", "Terraform", "GitHub Actions"],
            tools=["Git", "Linux", "VS Code", "Postman"],
            other=["REST APIs", "Microservices", "System Design", "CI/CD"],
        ),
        education=[
            EducationEntry(
                degree="Bachelor of Science",
                institution="University of California, Berkeley",
                specialization="Computer Science",
                start_year="2018",
                end_year="2022",
                grade_or_cgpa="3.85 GPA",
            ),
            EducationEntry(
                degree="High School Diploma",
                institution="Lowell High School",
                specialization="Science & Math",
                start_year="2014",
                end_year="2018",
                grade_or_cgpa="4.0 GPA",
            ),
        ],
        experience=[
            ExperienceEntry(
                job_title="Senior Backend Engineer",
                company="CloudScale Systems",
                employment_type="Full-time",
                location="San Francisco, CA (Hybrid)",
                start_date="Jan 2023",
                end_date="Present",
                description="Architected distributed APIs handling 50M monthly requests with 99.99% uptime.",
                technologies=["Python", "FastAPI", "PostgreSQL", "Redis", "Docker"],
            ),
            ExperienceEntry(
                job_title="Software Engineering Intern",
                company="NextGen Tech",
                employment_type="Internship",
                location="San Jose, CA",
                start_date="Jun 2022",
                end_date="Dec 2022",
                description="Built automated ETL data pipelines using Pandas and integrated Docker container CI/CD.",
                technologies=["Python", "Pandas", "Docker", "Git"],
            ),
        ],
        projects=[
            ProjectEntry(
                project_name="Distributed Task Queue System",
                description="Asynchronous task worker framework capable of executing 50k background tasks daily.",
                technologies=["Python", "Celery", "Redis", "Docker"],
                project_url="https://github.com/alexreed-dev/task-queue",
            ),
            ProjectEntry(
                project_name="Real-Time Analytics Dashboard",
                description="Low-latency telemetry streaming service using WebSockets and ClickHouse.",
                technologies=["FastAPI", "ClickHouse", "WebSockets", "React"],
                project_url="https://github.com/alexreed-dev/analytics-dash",
            ),
        ],
        certifications=[
            CertificationEntry(
                certification_name="AWS Certified Solutions Architect – Associate",
                issuing_organization="Amazon Web Services",
                issue_date="Nov 2023",
                credential_url="https://aws.amazon.com/verify/12345",
            ),
            CertificationEntry(
                certification_name="Certified Kubernetes Application Developer (CKAD)",
                issuing_organization="Cloud Native Computing Foundation",
                issue_date="May 2024",
                credential_url="https://cncf.io/verify/67890",
            ),
        ],
        achievements=[
            AchievementEntry(
                title="1st Place Winner — CalHacks 2021",
                category="Hackathon",
                organization="CalHacks Foundation",
            ),
            AchievementEntry(
                title="Dean's Honors List (All Semesters)",
                category="Academic",
                organization="UC Berkeley",
            ),
        ],
    )

    # 3. Persist CandidateProfile to database
    rp = persist_parsed_candidate_profile(db_session, resume.id, original)
    assert rp is not None
    assert rp.id is not None

    # 4. Reconstitute CandidateProfile from database
    reconstructed = reconstitute_candidate_profile(db_session, resume.id)
    assert reconstructed is not None
    assert isinstance(reconstructed, CandidateProfile)

    # 5. Assert 100% exact match across all fields
    orig_dump = original.model_dump()
    recon_dump = reconstructed.model_dump()

    # Compare Personal Information
    assert recon_dump["personal_information"] == orig_dump["personal_information"]

    # Compare Professional Summary
    assert recon_dump["professional_summary"] == orig_dump["professional_summary"]

    # Compare all 10 TechnicalSkills categories
    for cat in [
        "programming_languages", "frontend", "backend", "databases",
        "data_analytics", "machine_learning", "deep_learning",
        "cloud_devops", "tools", "other"
    ]:
        assert sorted(recon_dump["technical_skills"][cat]) == sorted(orig_dump["technical_skills"][cat]), f"Mismatch in {cat}"

    # Compare Education
    assert len(recon_dump["education"]) == len(orig_dump["education"])
    for i in range(len(orig_dump["education"])):
        assert recon_dump["education"][i] == orig_dump["education"][i]

    # Compare Experience
    assert len(recon_dump["experience"]) == len(orig_dump["experience"])
    for i in range(len(orig_dump["experience"])):
        assert recon_dump["experience"][i] == orig_dump["experience"][i]

    # Compare Projects
    assert len(recon_dump["projects"]) == len(orig_dump["projects"])
    for i in range(len(orig_dump["projects"])):
        assert recon_dump["projects"][i] == orig_dump["projects"][i]

    # Compare Certifications
    assert len(recon_dump["certifications"]) == len(orig_dump["certifications"])
    for i in range(len(orig_dump["certifications"])):
        assert recon_dump["certifications"][i] == orig_dump["certifications"][i]

    # Compare Achievements
    assert len(recon_dump["achievements"]) == len(orig_dump["achievements"])
    for i in range(len(orig_dump["achievements"])):
        assert recon_dump["achievements"][i] == orig_dump["achievements"][i]

    # Full structural equality assertion
    assert recon_dump == orig_dump


def test_candidate_profile_null_and_empty_roundtrip_fidelity(db_session):
    """
    Test round-trip preservation with null optional values and empty lists.
    Guarantees no crashes on sparse resumes.
    """
    profile = create_or_update_local_career_profile(
        db_session,
        CareerProfileCreate(
            full_name="Minimal User",
            career_status="Fresher",
            highest_education="Bachelor's",
            degree="Information Tech",
            institution="Local College",
            graduation_year=2025,
            primary_target_role="Junior Developer",
            preferred_job_type="Full-time",
            preferred_work_mode="On-site",
            preferred_locations=[],
        ),
    )

    resume = register_uploaded_resume(
        db_session,
        career_profile_id=profile.id,
        file_id="fedcba0987654321fedcba0987654321",
        original_filename="minimal.pdf",
        file_size=50000,
    )

    minimal_profile = CandidateProfile(
        personal_information=PersonalInformation(
            full_name="Minimal User",
            email=None,
            phone=None,
            linkedin=None,
            github=None,
            portfolio=None,
            location=None,
        ),
        professional_summary=None,
        technical_skills=TechnicalSkills(
            programming_languages=["Python"],
            frontend=[],
            backend=[],
            databases=[],
            data_analytics=[],
            machine_learning=[],
            deep_learning=[],
            cloud_devops=[],
            tools=[],
            other=[],
        ),
        education=[],
        experience=[],
        projects=[],
        certifications=[],
        achievements=[],
    )

    persist_parsed_candidate_profile(db_session, resume.id, minimal_profile)
    reconstructed = reconstitute_candidate_profile(db_session, resume.id)

    assert reconstructed is not None
    assert reconstructed.personal_information.email is None
    assert reconstructed.professional_summary is None
    assert reconstructed.technical_skills.programming_languages == ["Python"]
    assert reconstructed.technical_skills.databases == []
    assert reconstructed.education == []
    assert reconstructed.experience == []
    assert reconstructed.projects == []
    assert reconstructed.certifications == []
    assert reconstructed.achievements == []
    assert reconstructed.model_dump() == minimal_profile.model_dump()

