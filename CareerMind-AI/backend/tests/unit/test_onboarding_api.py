"""
Unit and integration tests for Career Profile Onboarding System (Phase C & D).

Covers:
1. GET /api/v1/onboarding/status on fresh database (returns False).
2. GET /api/v1/onboarding/profile when no profile exists (returns 404).
3. POST /api/v1/onboarding/profile successful registration (returns 201).
4. Validation: missing required fields (returns 422).
5. Validation: invalid career_status (returns 422).
6. Validation: invalid graduation_year (returns 422).
7. Validation: whitespace-only strings rejected (returns 422).
8. Duplicate registration prevention (returns 409 Conflict).
9. GET /api/v1/onboarding/status after registration (returns True with user info).
10. GET /api/v1/onboarding/profile retrieves created profile with exact fields.
11. PUT /api/v1/onboarding/profile updates profile and persists changes (returns 200).
12. PUT /api/v1/onboarding/profile when no profile exists (returns 404).
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database.base import Base
from database.session import get_db
from database.models.career_profile import CareerProfile

# In-memory SQLite for isolated test execution
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


VALID_PROFILE_PAYLOAD = {
    "full_name": "Shivam Kumar",
    "career_status": "Fresher",
    "highest_education": "Bachelor's Degree",
    "degree": "B.Tech Computer Science",
    "institution": "Indian Institute of Technology",
    "graduation_year": 2025,
    "primary_target_role": "Full Stack Software Engineer",
    "preferred_job_type": "Full-time",
    "preferred_work_mode": "Hybrid",
    "preferred_locations": ["Bangalore", "Hyderabad", "Remote"],
    "career_objective": "Aspiring engineer focused on building robust, scalable web architectures.",
}


def test_onboarding_status_empty_db(client):
    """Status should report false when no profile has been registered."""
    response = client.get("/api/v1/onboarding/status")
    assert response.status_code == 200
    data = response.json()
    assert data["onboarding_completed"] is False
    assert data["has_profile"] is False
    assert data["full_name"] is None
    assert data["primary_target_role"] is None


def test_get_profile_not_found(client):
    """Fetching profile before onboarding returns HTTP 404."""
    response = client.get("/api/v1/onboarding/profile")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_register_career_profile_success(client):
    """Successful registration creates profile and returns HTTP 201."""
    response = client.post("/api/v1/onboarding/profile", json=VALID_PROFILE_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert data["full_name"] == "Shivam Kumar"
    assert data["career_status"] == "Fresher"
    assert data["highest_education"] == "Bachelor's Degree"
    assert data["degree"] == "B.Tech Computer Science"
    assert data["institution"] == "Indian Institute of Technology"
    assert data["graduation_year"] == 2025
    assert data["primary_target_role"] == "Full Stack Software Engineer"
    assert data["preferred_job_type"] == "Full-time"
    assert data["preferred_work_mode"] == "Hybrid"
    assert data["preferred_locations"] == ["Bangalore", "Hyderabad", "Remote"]
    assert data["career_objective"] == "Aspiring engineer focused on building robust, scalable web architectures."
    assert data["onboarding_completed"] is True
    assert data["user_id"] == "local_user"
    assert "id" in data


def test_duplicate_profile_registration_returns_409(client):
    """Attempting to register twice returns HTTP 409 Conflict."""
    first_resp = client.post("/api/v1/onboarding/profile", json=VALID_PROFILE_PAYLOAD)
    assert first_resp.status_code == 201

    second_resp = client.post("/api/v1/onboarding/profile", json=VALID_PROFILE_PAYLOAD)
    assert second_resp.status_code == 409
    assert "already exists" in second_resp.json()["detail"].lower()


def test_onboarding_status_completed(client):
    """Status endpoint reflects completed onboarding with user summary."""
    client.post("/api/v1/onboarding/profile", json=VALID_PROFILE_PAYLOAD)

    status_resp = client.get("/api/v1/onboarding/status")
    assert status_resp.status_code == 200
    data = status_resp.json()
    assert data["onboarding_completed"] is True
    assert data["has_profile"] is True
    assert data["full_name"] == "Shivam Kumar"
    assert data["primary_target_role"] == "Full Stack Software Engineer"
    assert data["career_status"] == "Fresher"


def test_get_registered_profile(client):
    """Fetching profile returns the complete persisted profile."""
    client.post("/api/v1/onboarding/profile", json=VALID_PROFILE_PAYLOAD)

    get_resp = client.get("/api/v1/onboarding/profile")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["full_name"] == "Shivam Kumar"
    assert data["degree"] == "B.Tech Computer Science"


def test_update_registered_profile(client):
    """Updating profile fields returns HTTP 200 and persists updates."""
    client.post("/api/v1/onboarding/profile", json=VALID_PROFILE_PAYLOAD)

    update_payload = {
        "primary_target_role": "Lead Backend Architect",
        "preferred_work_mode": "Remote",
        "preferred_locations": ["Bangalore", "Remote"],
        "career_status": "Experienced",
    }
    put_resp = client.put("/api/v1/onboarding/profile", json=update_payload)
    assert put_resp.status_code == 200
    data = put_resp.json()
    assert data["primary_target_role"] == "Lead Backend Architect"
    assert data["preferred_work_mode"] == "Remote"
    assert data["preferred_locations"] == ["Bangalore", "Remote"]
    assert data["career_status"] == "Experienced"
    # Unchanged fields remain preserved
    assert data["full_name"] == "Shivam Kumar"
    assert data["degree"] == "B.Tech Computer Science"


def test_update_profile_not_found(client):
    """Updating when no profile exists returns HTTP 404."""
    update_payload = {"primary_target_role": "DevOps Engineer"}
    put_resp = client.put("/api/v1/onboarding/profile", json=update_payload)
    assert put_resp.status_code == 404
    assert "not found" in put_resp.json()["detail"].lower()


@pytest.mark.parametrize("invalid_status", ["SeniorExecutive", "Founder", "Other", ""])
def test_validation_invalid_career_status(client, invalid_status):
    """Invalid career status values are rejected with HTTP 422."""
    payload = {**VALID_PROFILE_PAYLOAD, "career_status": invalid_status}
    resp = client.post("/api/v1/onboarding/profile", json=payload)
    assert resp.status_code == 422


@pytest.mark.parametrize("invalid_year", [1960, 2045, -1, "not-a-year"])
def test_validation_invalid_graduation_year(client, invalid_year):
    """Out-of-range or non-numeric graduation year is rejected with HTTP 422."""
    payload = {**VALID_PROFILE_PAYLOAD, "graduation_year": invalid_year}
    resp = client.post("/api/v1/onboarding/profile", json=payload)
    assert resp.status_code == 422


@pytest.mark.parametrize("required_field", [
    "full_name",
    "career_status",
    "highest_education",
    "degree",
    "institution",
    "graduation_year",
    "primary_target_role",
])
def test_validation_missing_required_fields(client, required_field):
    """Omitting any required field returns HTTP 422."""
    payload = {k: v for k, v in VALID_PROFILE_PAYLOAD.items() if k != required_field}
    resp = client.post("/api/v1/onboarding/profile", json=payload)
    assert resp.status_code == 422


def test_validation_whitespace_only_strings_rejected(client):
    """Whitespace-only strings are rejected with HTTP 422."""
    payload = {**VALID_PROFILE_PAYLOAD, "full_name": "   "}
    resp = client.post("/api/v1/onboarding/profile", json=payload)
    assert resp.status_code == 422

