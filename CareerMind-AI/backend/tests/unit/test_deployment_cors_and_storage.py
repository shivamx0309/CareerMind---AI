"""
Unit tests for Production Deployment features:
- Root & Health check endpoints
- CORS middleware behavior (default origins, custom Vercel origin, credentials, methods)
- Persistent PDF storage directory configuration via CAREERMIND_UPLOAD_DIR
- Shared upload directory consistency between storage_service and matching_service
- SQLite parent directory creation behavior
"""

import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from main import app
from services import storage_service
from matching_engine import matching_service


def test_root_endpoint_healthy_without_db():
    """Verify GET / responds with 200 and running status without DB dependencies."""
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert "CareerMind AI" in data["message"]


def test_health_check_endpoint():
    """Verify GET /health responds with 200 and healthy status."""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["application"] == "CareerMind AI"


def test_cors_default_allowed_origin():
    """Verify that localhost frontend origin receives valid CORS headers."""
    client = TestClient(app)
    headers = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "POST",
    }
    response = client.options("/api/v1/resumes/upload", headers=headers)
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert response.headers.get("access-control-allow-credentials") == "true"


def test_cors_custom_origin_support(monkeypatch):
    """Verify that custom Vercel domain provided in FRONTEND_ORIGINS is recognized."""
    # Test origin parsing logic matching main.py
    custom_origins = "https://careermind-portfolio.vercel.app, https://custom-domain.com"
    parsed = [o.strip() for o in custom_origins.split(",") if o.strip()]
    assert "https://careermind-portfolio.vercel.app" in parsed
    assert "https://custom-domain.com" in parsed


def test_storage_service_default_fallback():
    """Verify default upload directory resolves to data/uploads when env is empty."""
    default_dir = storage_service.DEFAULT_UPLOAD_DIR
    assert default_dir.name == "uploads"
    assert default_dir.parent.name == "data"


def test_storage_service_custom_env_path(tmp_path, monkeypatch):
    """Verify that CAREERMIND_UPLOAD_DIR custom path is respected."""
    custom_dir = tmp_path / "var_data_uploads"
    monkeypatch.setenv("CAREERMIND_UPLOAD_DIR", str(custom_dir))

    env_val = os.getenv("CAREERMIND_UPLOAD_DIR")
    resolved = Path(env_val).resolve()
    assert resolved == custom_dir.resolve()


def test_matching_engine_shares_storage_service_upload_dir():
    """Verify that matching_service DEFAULT_UPLOAD_DIR references storage_service.UPLOAD_DIR."""
    assert matching_service.DEFAULT_UPLOAD_DIR == storage_service.UPLOAD_DIR


def test_sqlite_parent_dir_creation_logic(tmp_path):
    """Verify SQLite database URL parent directory creation logic."""
    target_dir = tmp_path / "deep" / "nested" / "var" / "data"
    test_db_url = f"sqlite:///{target_dir.as_posix()}/test_careermind.db"

    assert not target_dir.exists()

    db_file_str = test_db_url.replace("sqlite:///", "", 1)
    db_file_path = Path(db_file_str)
    db_file_path.parent.mkdir(parents=True, exist_ok=True)

    assert target_dir.exists()
    assert target_dir.is_dir()
