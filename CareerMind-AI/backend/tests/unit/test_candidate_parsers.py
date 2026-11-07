"""
Unit tests for resume information parsing modules.

Tests independently:
- Contact parser (Name, email, phone, LinkedIn, GitHub, portfolio, location)
- Skills parser (10 distinct categories, boundary protection, deduplication)
- Education parser (Degrees, institutions, specializations, graduation years, GPA/CGPA, multiple entries)
- Experience parser (Job title, company, dates, description, technologies, multiple entries)
- Project parser (Project name, description, technologies, project URL, multiple entries)
- Certifications parser (Certifications, issuing organization, dates, URLs)
- Section segmenter (Standard and unrecognized resume sections)
- Information extractor orchestrator (End-to-end integration and empty text handling)
"""

import pytest
from resume_engine.section_segmenter import segment_resume_sections
from resume_engine.contact_parser import (
    extract_full_name,
    extract_email,
    extract_phone,
    extract_linkedin,
    extract_github,
    extract_portfolio,
    extract_location,
    parse_contact_information,
)
from resume_engine.skills_parser import parse_technical_skills
from resume_engine.education_parser import (
    parse_education_entries,
    extract_degree_and_specialization,
    extract_years,
    extract_grade,
)
from resume_engine.experience_parser import (
    parse_experience_entries,
    parse_title_and_company,
    extract_employment_type,
)
from resume_engine.project_parser import (
    parse_project_entries,
    match_project_url,
)
from resume_engine.certifications_parser import (
    parse_certification_entries,
    parse_achievement_entries,
    extract_issuing_organization,
)
from resume_engine.information_extractor import extract_candidate_profile
from schemas.candidate_schema import CandidateProfile


# ============================================================================
# 1. Section Segmenter Tests
# ============================================================================

def test_segment_resume_standard_sections():
    sample_text = """
    Jane Doe
    jane@example.com

    Professional Summary
    Experienced software engineer with 5 years of backend development.

    Technical Skills
    Python, FastAPI, Docker, PostgreSQL

    Work Experience
    Senior Developer — Acme Corp
    2021 - Present
    • Built microservices.

    Projects
    Career Intelligence Platform
    Python, FastAPI
    • Built automated resume analyzer.

    Education
    Bachelor of Science in Computer Science
    MIT, 2017 - 2021

    Certifications
    AWS Certified Solutions Architect (2022)
    """
    sections = segment_resume_sections(sample_text)
    assert len(sections["header"]) >= 2
    assert "Experienced software engineer" in " ".join(sections["summary"])
    assert "FastAPI" in " ".join(sections["skills"])
    assert "Senior Developer" in " ".join(sections["experience"])
    assert "Career Intelligence Platform" in " ".join(sections["projects"])
    assert "Bachelor of Science" in " ".join(sections["education"])
    assert "AWS Certified Solutions Architect" in " ".join(sections["certifications"])


def test_segment_resume_unrecognized_sections():
    sample_text = """
    John Smith
    john@example.com

    Hobbies:
    Reading, playing chess, competitive swimming.

    Volunteer Work:
    Mentored high school students in programming.
    """
    sections = segment_resume_sections(sample_text)
    assert len(sections["header"]) >= 2
    # Unrecognized sections are categorized under other
    assert any("chess" in line for line in sections["other"])


def test_segment_resume_empty_text():
    sections = segment_resume_sections("")
    for key, val in sections.items():
        assert val == []


# ============================================================================
# 2. Contact and Personal Information Tests
# ============================================================================

def test_extract_full_name_standard():
    lines = ["SHIVAM KUMAR SINGH", "918887602317", "edu.shivam0903@gmail.com"]
    name = extract_full_name(lines)
    assert name == "Shivam Kumar Singh"


def test_extract_full_name_mixed_case():
    lines = ["Jane M. Doe", "jane.doe@example.com", "+1-555-123-4567"]
    name = extract_full_name(lines)
    assert name == "Jane M. Doe"


def test_extract_full_name_rejects_headings_and_roles():
    lines = ["Curriculum Vitae", "Senior Software Engineer", "Summary", "John Doe"]
    name = extract_full_name(lines)
    assert name == "John Doe"


def test_extract_full_name_missing():
    lines = ["john@example.com", "+1-555-123-4567", "https://linkedin.com/in/john"]
    name = extract_full_name(lines)
    assert name is None


def test_extract_email_standard():
    text = "Please reach out to edu.shivam0903@gmail.com for questions."
    assert extract_email(text) == "edu.shivam0903@gmail.com"


def test_extract_email_with_special_characters():
    text = "Contact: john.smith+careers@company.co.uk."
    assert extract_email(text) == "john.smith+careers@company.co.uk"


def test_extract_email_from_mailto_link():
    text = "# edu.shivam0903"
    links = ["mailto:edu.shivam0903@gmail.com?subject=Opportunity"]
    assert extract_email(text, links=links) == "edu.shivam0903@gmail.com"


def test_extract_email_missing():
    assert extract_email("No email here") is None


def test_extract_phone_international():
    assert extract_phone("Phone: +91 8887602317") in ("+918887602317", "+91 8887602317", "918887602317")


def test_extract_phone_us_format():
    phone = extract_phone("Call me at (555) 234-5678 or anytime.")
    assert phone is not None
    assert "555" in phone and "234" in phone


def test_extract_phone_from_tel_link():
    links = ["tel:+918887602317"]
    assert extract_phone("My Phone", links=links) == "+918887602317"


def test_extract_phone_does_not_match_years():
    text = "Graduated 2020 - 2024 with distinction."
    assert extract_phone(text) is None


def test_extract_linkedin_from_text():
    text = "Profile: https://www.linkedin.com/in/shivam-singh-123/ on LinkedIn"
    assert extract_linkedin(text) == "https://www.linkedin.com/in/shivam-singh-123"


def test_extract_linkedin_from_links():
    links = ["https://www.linkedin.com/in/shivam-kumar-singh-2b082a332/?locale=en_US"]
    assert extract_linkedin("ï LinkedIn", links=links) == "https://www.linkedin.com/in/shivam-kumar-singh-2b082a332"


def test_extract_github_from_text():
    text = "Check out my code at https://github.com/shivamx0309"
    assert extract_github(text) == "https://github.com/shivamx0309"


def test_extract_github_profile_link():
    links = [
        "https://github.com/shivamx0309/Employee-Attrition-Analysis",
        "https://github.com/shivamx0309",
    ]
    assert extract_github("§ GitHub", links=links) == "https://github.com/shivamx0309"


def test_extract_portfolio():
    text = "Portfolio: https://shivam-portfolio.vercel.app"
    assert extract_portfolio(text) == "https://shivam-portfolio.vercel.app"


def test_extract_location_explicit():
    lines = ["John Doe", "Location: San Francisco, CA"]
    assert extract_location(lines) == "San Francisco, CA"


def test_extract_location_implicit():
    lines = ["John Doe", "Agra, India", "john@example.com"]
    assert extract_location(lines) == "Agra, India"


def test_parse_contact_missing_fields_are_null():
    info = parse_contact_information([], "No contact details")
    assert info.full_name is None
    assert info.email is None
    assert info.phone is None
    assert info.linkedin is None
    assert info.github is None
    assert info.portfolio is None
    assert info.location is None


# ============================================================================
# 3. Technical Skills Parser Tests
# ============================================================================

def test_skills_categorization_ten_domains():
    skills_text = """
    Languages: Python, SQL, Java, TypeScript, C++
    Frontend: React, Next.js, Tailwind CSS, HTML, CSS
    Backend: FastAPI, Django, Express, Node.js
    Databases: PostgreSQL, MongoDB, Redis, Supabase
    Analytics: Pandas, NumPy, Power BI, Excel, EDA
    ML: Scikit-learn, Regression, Classification, Random Forest
    DL: PyTorch, TensorFlow, Hugging Face, LLMs, Generative AI
    Cloud: Docker, Kubernetes, AWS, GitHub Actions
    Tools: Git, GitHub, VS Code, Postman
    Other: Problem Solving, Data Structures, Algorithms, DSA
    """
    skills = parse_technical_skills(skills_text.splitlines(), skills_text)

    assert "Python" in skills.programming_languages
    assert "SQL" in skills.programming_languages
    assert "TypeScript" in skills.programming_languages

    assert "React" in skills.frontend
    assert "Next.js" in skills.frontend
    assert "Tailwind CSS" in skills.frontend

    assert "FastAPI" in skills.backend
    assert "PostgreSQL" in skills.databases
    assert "Pandas" in skills.data_analytics
    assert "Scikit-learn" in skills.machine_learning
    assert "PyTorch" in skills.deep_learning
    assert "Docker" in skills.cloud_devops
    assert "VS Code" in skills.tools
    assert "Data Structures & Algorithms" in skills.other


def test_skills_no_false_positives():
    # Make sure common words don't match short skills
    text = "Managed communications for the company, providing great customer service and continuous support."
    skills = parse_technical_skills(text.splitlines(), text)
    # Shouldn't match C, R, Go, etc.
    assert "C" not in skills.programming_languages
    assert "R" not in skills.programming_languages
    assert "Go" not in skills.programming_languages


def test_skills_deduplication():
    text = "Python, python, PYTHON, SQL, Sql, sql"
    skills = parse_technical_skills(text.splitlines(), text)
    assert skills.programming_languages.count("Python") == 1
    assert skills.programming_languages.count("SQL") == 1


def test_skills_empty():
    skills = parse_technical_skills([], "")
    assert skills.programming_languages == []
    assert skills.frontend == []
    assert skills.backend == []
    assert skills.databases == []
    assert skills.data_analytics == []
    assert skills.machine_learning == []
    assert skills.deep_learning == []
    assert skills.cloud_devops == []
    assert skills.tools == []
    assert skills.other == []


# ============================================================================
# 4. Education Parser Tests
# ============================================================================

def test_education_single_entry():
    lines = [
        "Bachelor of Engineering (Computer Science Engineering)",
        "2022–2026",
        "Institute of Engineering and Technology, Agra",
    ]
    entries = parse_education_entries(lines)
    assert len(entries) == 1
    assert entries[0].degree == "Bachelor of Engineering"
    assert entries[0].institution == "Institute of Engineering and Technology, Agra"
    assert entries[0].specialization == "Computer Science Engineering"
    assert entries[0].start_year == "2022"
    assert entries[0].end_year == "2026"
    assert entries[0].grade_or_cgpa is None


def test_education_multiple_entries_with_grades():
    lines = [
        "Master of Science in Software Engineering",
        "Stanford University",
        "2020 - 2022",
        "GPA: 3.9/4.0",
        "",
        "Bachelor of Technology in Computer Science",
        "National Institute of Technology",
        "2016 - 2020",
        "CGPA: 8.8 / 10",
    ]
    entries = parse_education_entries(lines)
    assert len(entries) == 2
    assert entries[0].degree == "Master of Science"
    assert "Stanford" in entries[0].institution
    assert entries[0].grade_or_cgpa == "3.9/4.0"

    assert entries[1].degree == "Bachelor of Technology"
    assert "National Institute of Technology" in entries[1].institution
    assert "8.8" in entries[1].grade_or_cgpa


def test_education_empty():
    assert parse_education_entries([]) == []


# ============================================================================
# 5. Experience Parser Tests
# ============================================================================

def test_experience_single_entry():
    lines = [
        "Tech Innovation Associate — Humppl",
        "Jun 2026 – Present",
        "• Developed and enhanced CRM modules using Next.js, TypeScript, Tailwind CSS and Supabase.",
        "• Collaborated using Git, GitHub, feature branches and pull requests.",
        "• Worked with PostgreSQL (Supabase) for database operations and application integration.",
    ]
    entries = parse_experience_entries(lines)
    assert len(entries) == 1
    assert entries[0].job_title == "Tech Innovation Associate"
    assert entries[0].company == "Humppl"
    assert entries[0].start_date == "Jun 2026"
    assert entries[0].end_date == "Present"
    assert entries[0].employment_type == "Associate"
    assert "Next.js" in entries[0].technologies
    assert "TypeScript" in entries[0].technologies
    assert "PostgreSQL" in entries[0].technologies
    assert "Supabase" in entries[0].technologies


def test_experience_multiple_entries():
    lines = [
        "Software Engineer — Acme Corp",
        "Jan 2022 - Dec 2023",
        "• Developed Python backend microservices.",
        "Summer Intern — Tech Corp",
        "May 2021 - Aug 2021",
        "• Automated tests using Selenium and Python.",
    ]
    entries = parse_experience_entries(lines)
    assert len(entries) == 2
    assert entries[0].job_title == "Software Engineer"
    assert entries[0].company == "Acme Corp"
    assert entries[1].job_title == "Summer Intern"
    assert entries[1].company == "Tech Corp"
    assert entries[1].employment_type == "Internship"


def test_experience_empty():
    assert parse_experience_entries([]) == []


# ============================================================================
# 6. Projects Parser Tests
# ============================================================================

def test_project_single_entry():
    lines = [
        "Employee Attrition Prediction Model",
        "§ GitHub",
        "Python — Pandas — NumPy — Scikit-learn — Machine Learning",
        "• Developed an employee attrition prediction model using Python and Scikit-learn.",
        "• Evaluated performance using Accuracy and Confusion Matrix.",
    ]
    links = ["https://github.com/shivamx0309/Employee-Attrition-Analysis"]
    entries = parse_project_entries(lines, links=links)
    assert len(entries) == 1
    assert entries[0].project_name == "Employee Attrition Prediction Model"
    assert entries[0].project_url == "https://github.com/shivamx0309/Employee-Attrition-Analysis"
    assert "Python" in entries[0].technologies
    assert "Pandas" in entries[0].technologies
    assert "Scikit-learn" in entries[0].technologies
    assert "Developed an employee attrition prediction model" in entries[0].description


def test_project_multiple_entries():
    lines = [
        "Personal Portfolio",
        "React — Tailwind CSS",
        "• Built interactive personal website: https://myportfolio.dev",
        "Sales Analytics Dashboard",
        "Python — SQL — Power BI",
        "• Built automated BI dashboard with KPI drill-downs.",
    ]
    entries = parse_project_entries(lines)
    assert len(entries) == 2
    assert entries[0].project_name == "Personal Portfolio"
    assert entries[0].project_url == "https://myportfolio.dev"
    assert "React" in entries[0].technologies

    assert entries[1].project_name == "Sales Analytics Dashboard"
    assert "Power BI" in entries[1].technologies


def test_projects_empty():
    assert parse_project_entries([]) == []


# ============================================================================
# 7. Certifications Parser Tests
# ============================================================================

def test_certifications_parsing():
    lines = [
        "• Completed Accenture Data Analytics & Visualization Job Simulation.",
        "• Completed Tata GenAI Powered Data Analytics Job Simulation.",
        "• AWS Certified Solutions Architect (2023) - https://aws.amazon.com/verify/123",
    ]
    entries = parse_certification_entries(lines)
    assert len(entries) == 3
    assert entries[0].issuing_organization == "Accenture"
    assert "Data Analytics & Visualization" in entries[0].certification_name

    assert entries[1].issuing_organization == "Tata"
    assert "GenAI" in entries[1].certification_name

    assert entries[2].issuing_organization == "Amazon Web Services"
    assert entries[2].issue_date == "2023"
    assert entries[2].credential_url == "https://aws.amazon.com/verify/123"


def test_certifications_empty():
    assert parse_certification_entries([]) == []


# ============================================================================
# 8. Information Extractor Orchestrator Tests
# ============================================================================

def test_extract_candidate_profile_empty_text():
    profile = extract_candidate_profile("")
    assert isinstance(profile, CandidateProfile)
    assert profile.personal_information.full_name is None
    assert profile.professional_summary is None
    assert profile.technical_skills.programming_languages == []
    assert profile.education == []
    assert profile.experience == []
    assert profile.projects == []
    assert profile.certifications == []
    assert profile.achievements == []


# ============================================================================
# 9. Phase 4.1 Parser Accuracy & Quality Improvement Tests
# ============================================================================

def test_experience_multiline_header_with_location_and_remote():
    """Verify multi-line header properly associates employer, title, and location."""
    lines = [
        "Humppl",
        "Remote",
        "Software Development Engineer",
        "June 2026 – Sep 2026",
        "• Developed CRM modules using Next.js and Supabase.",
        "• Performed regression testing on backend endpoints.",
        "",
        "Hindalco Industries Limited",
        "Renukoot, Uttar Pradesh",
        "Summer Intern",
        "July 2024 – August 2024",
        "• Conducted operational data analysis.",
    ]
    entries = parse_experience_entries(lines)
    assert len(entries) == 2

    # Job 1
    assert entries[0].company == "Humppl"
    assert entries[0].job_title == "Software Development Engineer"
    assert entries[0].location == "Remote"
    assert entries[0].start_date == "June 2026"
    assert entries[0].end_date == "Sep 2026"
    assert "Supabase" in entries[0].technologies
    # Verify regression testing did NOT trigger Regression (ML)
    assert "Regression" not in entries[0].technologies

    # Job 2
    assert entries[1].company == "Hindalco Industries Limited"
    assert entries[1].job_title == "Summer Intern"
    assert entries[1].location == "Renukoot, Uttar Pradesh"
    assert entries[1].employment_type == "Internship"
    assert entries[1].start_date == "July 2024"
    assert entries[1].end_date == "August 2024"


def test_project_strips_standalone_link_labels():
    """Verify that 'Live Demo', 'GitHub', 'Preview' are stripped from project descriptions."""
    lines = [
        "Real-Time Chat Application",
        "Live Demo | GitHub",
        "React — Node.js — Socket.io",
        "• Developed a real-time chat application with WebSockets.",
        "• Optimized chat latency by 40%.",
    ]
    links = [
        "https://chatapp-demo.vercel.app",
        "https://github.com/shivamx0309/realtime-chat",
    ]
    entries = parse_project_entries(lines, links=links)
    assert len(entries) == 1
    assert entries[0].project_name == "Real-Time Chat Application"
    # Description should NOT contain "Live Demo" or "GitHub" labels
    assert "Live Demo" not in entries[0].description
    assert "GitHub" not in entries[0].description
    assert "Developed a real-time chat application" in entries[0].description
    # Technologies extracted
    assert "React" in entries[0].technologies
    assert "Socket.IO" in entries[0].technologies
    # URL matched from links
    assert entries[0].project_url in links


def test_skills_canonicalization_and_overlap_suppression():
    """Verify canonical naming and suppression of substrings."""
    lines = [
        "Technical Skills",
        "Languages: C++, Python, JavaScript, TypeScript",
        "Frontend: React.js, Next.js, Tailwind CSS",
        "Backend & DB: REST APIs, Supabase, PostgreSQL",
        "Core Concepts: Data Structures & Algorithms, DSA, Algorithms, Object Oriented Programming",
    ]
    skills = parse_technical_skills(lines)
    # React.js canonicalized to React
    assert "React" in skills.frontend
    assert "React.js" not in skills.frontend
    # REST APIs canonicalized to REST API
    assert "REST API" in skills.backend
    # Supabase in databases
    assert "Supabase" in skills.databases
    # DSA and Algorithms suppressed in favor of Data Structures & Algorithms
    assert "Data Structures & Algorithms" in skills.other
    assert "DSA" not in skills.other
    assert "Algorithms" not in skills.other


def test_data_analytics_detected_from_experience():
    """Verify operational data analysis triggers Data Analytics skill."""
    lines = [
        "Work Experience",
        "Summer Intern — Hindalco Industries Limited",
        "July 2024 – August 2024",
        "• Conducted operational data analysis across plant telemetry.",
    ]
    skills = parse_technical_skills([], full_text="\n".join(lines))
    assert "Data Analytics" in skills.data_analytics


def test_achievements_parsing():
    """Verify achievements categorization and parsing."""
    lines = [
        "• Received Badge of Honour from Humppl for exemplary performance.",
        "• Secured 2nd Place in College Coding Hackathon 2024.",
        "• Solved 300+ problems on LeetCode.",
    ]
    achievements = parse_achievement_entries(lines)
    assert len(achievements) == 3
    assert achievements[0].category == "Award / Recognition"
    assert achievements[0].organization == "Humppl"
    assert achievements[1].category == "Competition"
    assert achievements[2].category == "Coding Milestone"


def test_section_segmenter_achievements_vs_certifications():
    """Verify section segmenter splits achievements and certifications into distinct lists."""
    text = """
    Jane Doe
    jane@example.com

    ACHIEVEMENTS
    • Badge of Honour from Humppl
    • Solved 200+ problems on LeetCode

    CERTIFICATIONS & JOB SIMULATIONS
    • Deloitte Technology Job Simulation
    • Full Stack Web Development – Apna College
    """
    sections = segment_resume_sections(text)
    assert len(sections["achievements"]) >= 2
    assert any("Badge of Honour" in l for l in sections["achievements"])
    assert len(sections["certifications"]) >= 2
    assert any("Deloitte" in l for l in sections["certifications"])


def test_extract_candidate_profile_null_summary_when_absent():
    """Verify that when resume has no summary, professional_summary is None (no hallucination)."""
    text = """
    Jane Doe
    jane@example.com
    +1 555-123-4567

    EXPERIENCE
    Software Engineer — Acme Corp
    2022 - Present
    • Developed Python backend microservices.

    EDUCATION
    B.Tech in Computer Science
    IIT Delhi
    2018 - 2022
    """
    profile = extract_candidate_profile(text)
    assert profile.professional_summary is None
    assert profile.personal_information.full_name == "Jane Doe"
    assert len(profile.experience) == 1
    assert len(profile.education) == 1


def test_extract_candidate_profile_with_achievements():
    """Verify full orchestrator handles achievements alongside certifications."""
    text = """
    Jane Doe
    jane@example.com

    EXPERIENCE
    Software Engineer — Acme Corp
    2022 - Present
    • Built microservices.

    ACHIEVEMENTS
    • 1st Place Winner at Global Hackathon 2024

    CERTIFICATIONS
    • AWS Certified Cloud Practitioner
    """
    profile = extract_candidate_profile(text)
    assert len(profile.achievements) == 1
    assert profile.achievements[0].category == "Competition"
    assert len(profile.certifications) == 1
    assert profile.certifications[0].certification_name == "AWS Certified Cloud Practitioner"


