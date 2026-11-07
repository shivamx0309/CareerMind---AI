"""
Integration tests for the Resume Information Parsing API:
POST /api/v1/resumes/{file_id}/parse

Covers:
1. Successful resume parsing into CandidateProfile JSON.
2. Invalid file ID format validation (HTTP 400).
3. Missing PDF file (HTTP 404).
4. Empty-text PDF document (HTTP 422).
5. Corrupted PDF document (HTTP 422).
6. End-to-end workflow (Upload -> Extract -> Parse).
7. Regression test for existing Upload API (POST /api/v1/resumes/upload).
8. Regression test for existing Text Extraction API (POST /api/v1/resumes/{file_id}/extract).
"""

import io
import uuid
import pymupdf
from fastapi.testclient import TestClient

from main import app
from api.v1.endpoints import resume as resume_endpoint


client = TestClient(app)


def create_sample_resume_pdf() -> bytes:
    """Create a realistic in-memory candidate resume PDF for testing."""
    document = pymupdf.open()
    page = document.new_page()

    content = (
        "SHIVAM KUMAR SINGH\n"
        "Phone: +91 8887602317\n"
        "Email: edu.shivam0903@gmail.com\n"
        "LinkedIn: https://www.linkedin.com/in/shivam-kumar-singh-2b082a332\n"
        "GitHub: https://github.com/shivamx0309\n"
        "\n"
        "Professional Summary\n"
        "Computer Science Engineering student skilled in SQL, Python, Excel, Power BI, and Data Analytics. "
        "Passionate about transforming data into actionable business insights.\n"
        "\n"
        "Technical Skills\n"
        "Programming: Python, SQL, Java\n"
        "Analytics: Pandas, NumPy, Power BI, Excel, EDA\n"
        "Databases: PostgreSQL, MySQL, MongoDB\n"
        "Machine Learning: Scikit-learn, Regression, Classification\n"
        "Tools: Git, GitHub, VS Code, Jupyter Notebook\n"
        "\n"
        "Work Experience\n"
        "Tech Innovation Associate — Humppl\n"
        "Jun 2026 – Present\n"
        "• Developed and enhanced CRM modules using Next.js, TypeScript, Tailwind CSS and Supabase.\n"
        "• Worked with PostgreSQL for database operations.\n"
        "\n"
        "Projects\n"
        "Employee Attrition Prediction Model\n"
        "Python — Pandas — NumPy — Scikit-learn — Machine Learning\n"
        "• Developed an employee attrition prediction model using Python and Scikit-learn.\n"
        "• Repository: https://github.com/shivamx0309/Employee-Attrition-Analysis\n"
        "\n"
        "Education\n"
        "Bachelor of Engineering (Computer Science Engineering)\n"
        "2022–2026\n"
        "Institute of Engineering and Technology, Agra\n"
        "\n"
        "Certifications\n"
        "• Completed Accenture Data Analytics & Visualization Job Simulation.\n"
        "• AWS Certified Solutions Architect (2023)\n"
    )

    page.insert_text((50, 50), content, fontsize=10)
    pdf_bytes = document.tobytes()
    document.close()
    return pdf_bytes


def create_empty_text_pdf() -> bytes:
    """Create a valid PDF with one blank page."""
    document = pymupdf.open()
    document.new_page()
    pdf_bytes = document.tobytes()
    document.close()
    return pdf_bytes


# 1. Successful Resume Parsing
def test_parse_valid_resume_success(monkeypatch, tmp_path):
    monkeypatch.setattr(resume_endpoint, "UPLOAD_DIR", tmp_path)

    file_id = uuid.uuid4().hex
    pdf_bytes = create_sample_resume_pdf()
    pdf_file = tmp_path / f"{file_id}.pdf"
    pdf_file.write_bytes(pdf_bytes)

    response = client.post(f"/api/v1/resumes/{file_id}/parse")
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["file_id"] == file_id

    candidate = data["candidate"]
    # Personal Info
    assert candidate["personal_information"]["full_name"] == "Shivam Kumar Singh"
    assert candidate["personal_information"]["email"] == "edu.shivam0903@gmail.com"
    assert "8887602317" in candidate["personal_information"]["phone"]
    assert "linkedin.com/in/shivam-kumar-singh" in candidate["personal_information"]["linkedin"]
    assert "github.com/shivamx0309" in candidate["personal_information"]["github"]

    # Summary
    assert candidate["professional_summary"] is not None
    assert "Computer Science Engineering student" in candidate["professional_summary"]

    # Technical Skills
    skills = candidate["technical_skills"]
    assert "Python" in skills["programming_languages"]
    assert "SQL" in skills["programming_languages"]
    assert "Pandas" in skills["data_analytics"]
    assert "Scikit-learn" in skills["machine_learning"]
    assert "PostgreSQL" in skills["databases"]

    # Education
    assert len(candidate["education"]) >= 1
    assert candidate["education"][0]["degree"] == "Bachelor of Engineering"
    assert "Agra" in candidate["education"][0]["institution"]
    assert candidate["education"][0]["start_year"] == "2022"
    assert candidate["education"][0]["end_year"] == "2026"

    # Experience
    assert len(candidate["experience"]) >= 1
    assert candidate["experience"][0]["job_title"] == "Tech Innovation Associate"
    assert candidate["experience"][0]["company"] == "Humppl"
    assert candidate["experience"][0]["start_date"] == "Jun 2026"
    assert candidate["experience"][0]["end_date"] == "Present"

    # Projects
    assert len(candidate["projects"]) >= 1
    assert candidate["projects"][0]["project_name"] == "Employee Attrition Prediction Model"
    assert "Employee-Attrition-Analysis" in candidate["projects"][0]["project_url"]

    # Certifications
    assert len(candidate["certifications"]) >= 1
    assert any(c["issuing_organization"] == "Accenture" for c in candidate["certifications"])


# 2. Invalid file ID returns HTTP 400
def test_parse_invalid_file_id_returns_400(monkeypatch, tmp_path):
    monkeypatch.setattr(resume_endpoint, "UPLOAD_DIR", tmp_path)

    # Invalid non-hex string
    response = client.post("/api/v1/resumes/not-a-valid-hex-uuid/parse")
    assert response.status_code == 400
    assert "Invalid file ID format" in response.json()["detail"]

    # Too short
    response = client.post("/api/v1/resumes/123/parse")
    assert response.status_code == 400

    # Path traversal pattern
    response = client.post("/api/v1/resumes/bad..uuid/parse")
    assert response.status_code == 400


# 3. Missing PDF file returns HTTP 404
def test_parse_missing_pdf_returns_404(monkeypatch, tmp_path):
    monkeypatch.setattr(resume_endpoint, "UPLOAD_DIR", tmp_path)

    non_existent_id = uuid.uuid4().hex
    response = client.post(f"/api/v1/resumes/{non_existent_id}/parse")
    assert response.status_code == 404
    assert "Resume file not found" in response.json()["detail"]


# 4. Empty-text PDF returns HTTP 422
def test_parse_empty_text_pdf_returns_422(monkeypatch, tmp_path):
    monkeypatch.setattr(resume_endpoint, "UPLOAD_DIR", tmp_path)

    file_id = uuid.uuid4().hex
    pdf_bytes = create_empty_text_pdf()
    pdf_file = tmp_path / f"{file_id}.pdf"
    pdf_file.write_bytes(pdf_bytes)

    response = client.post(f"/api/v1/resumes/{file_id}/parse")
    assert response.status_code == 422
    assert "No readable text found" in response.json()["detail"]


# 5. Corrupted PDF returns HTTP 422
def test_parse_corrupted_pdf_returns_422(monkeypatch, tmp_path):
    monkeypatch.setattr(resume_endpoint, "UPLOAD_DIR", tmp_path)

    file_id = uuid.uuid4().hex
    pdf_file = tmp_path / f"{file_id}.pdf"
    pdf_file.write_bytes(b"%PDF-1.4\nCORRUPTED_BYTES_HERE_NOT_A_REAL_PDF")

    response = client.post(f"/api/v1/resumes/{file_id}/parse")
    assert response.status_code == 422


# 6. End-to-end workflow: Upload -> Extract -> Parse
def test_end_to_end_upload_extract_parse(monkeypatch, tmp_path):
    monkeypatch.setattr(resume_endpoint, "UPLOAD_DIR", tmp_path)

    pdf_bytes = create_sample_resume_pdf()

    # Step 1: Upload
    upload_response = client.post(
        "/api/v1/resumes/upload",
        files={"file": ("candidate_resume.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )
    assert upload_response.status_code == 201
    file_id = upload_response.json()["file_id"]

    # Step 2: Extract text
    extract_response = client.post(f"/api/v1/resumes/{file_id}/extract")
    assert extract_response.status_code == 200
    extract_data = extract_response.json()
    assert extract_data["success"] is True
    assert "SHIVAM KUMAR SINGH" in extract_data["full_text"]

    # Step 3: Parse profile
    parse_response = client.post(f"/api/v1/resumes/{file_id}/parse")
    assert parse_response.status_code == 200
    parse_data = parse_response.json()
    assert parse_data["success"] is True
    assert parse_data["file_id"] == file_id
    assert parse_data["candidate"]["personal_information"]["full_name"] == "Shivam Kumar Singh"


# 7. Regression test for existing Upload API
def test_regression_upload_api(monkeypatch, tmp_path):
    monkeypatch.setattr(resume_endpoint, "UPLOAD_DIR", tmp_path)

    pdf_bytes = create_sample_resume_pdf()
    response = client.post(
        "/api/v1/resumes/upload",
        files={"file": ("test.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )
    assert response.status_code == 201
    assert response.json()["success"] is True
    assert response.json()["extraction_status"] == "pending"


# 8. Regression test for existing Extraction API
def test_regression_extraction_api(monkeypatch, tmp_path):
    monkeypatch.setattr(resume_endpoint, "UPLOAD_DIR", tmp_path)

    file_id = uuid.uuid4().hex
    pdf_bytes = create_sample_resume_pdf()
    (tmp_path / f"{file_id}.pdf").write_bytes(pdf_bytes)

    response = client.post(f"/api/v1/resumes/{file_id}/extract")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["extraction_status"] == "completed"

