"""
Pydantic schemas for structured candidate information extracted from resumes.
"""

from pydantic import BaseModel, Field


class PersonalInformation(BaseModel):
    """Candidate personal and contact details."""

    full_name: str | None = Field(
        default=None, description="Full name of the candidate"
    )
    email: str | None = Field(
        default=None, description="Primary contact email address"
    )
    phone: str | None = Field(
        default=None, description="Primary contact phone number"
    )
    linkedin: str | None = Field(
        default=None, description="LinkedIn profile URL or handle"
    )
    github: str | None = Field(
        default=None, description="GitHub profile URL or handle"
    )
    portfolio: str | None = Field(
        default=None, description="Personal website or portfolio URL"
    )
    location: str | None = Field(
        default=None, description="City, state, or country of residence"
    )


class TechnicalSkills(BaseModel):
    """Categorized technical skills identified in the candidate's resume."""

    programming_languages: list[str] = Field(
        default_factory=list, description="Core programming languages"
    )
    frontend: list[str] = Field(
        default_factory=list, description="Frontend frameworks and UI libraries"
    )
    backend: list[str] = Field(
        default_factory=list, description="Backend frameworks and server technologies"
    )
    databases: list[str] = Field(
        default_factory=list, description="Relational and NoSQL database management systems"
    )
    data_analytics: list[str] = Field(
        default_factory=list, description="Data analysis, visualization, and BI tools"
    )
    machine_learning: list[str] = Field(
        default_factory=list, description="Classical ML algorithms and frameworks"
    )
    deep_learning: list[str] = Field(
        default_factory=list, description="Deep neural networks, NLP, and AI architectures"
    )
    cloud_devops: list[str] = Field(
        default_factory=list, description="Cloud providers, CI/CD, and DevOps tooling"
    )
    tools: list[str] = Field(
        default_factory=list, description="Developer tools, IDEs, and version control"
    )
    other: list[str] = Field(
        default_factory=list, description="Other software engineering concepts and skills"
    )


class EducationEntry(BaseModel):
    """Educational qualification entry."""

    degree: str | None = Field(
        default=None, description="Degree or diploma earned (e.g., Bachelor of Engineering)"
    )
    institution: str | None = Field(
        default=None, description="College, university, or school attended"
    )
    specialization: str | None = Field(
        default=None, description="Major, field of study, or stream"
    )
    start_year: str | None = Field(
        default=None, description="Year study commenced"
    )
    end_year: str | None = Field(
        default=None, description="Year completed or expected graduation"
    )
    grade_or_cgpa: str | None = Field(
        default=None, description="Academic performance (CGPA, GPA, or percentage)"
    )


class ExperienceEntry(BaseModel):
    """Professional work experience or internship entry."""

    job_title: str | None = Field(
        default=None, description="Designation or job title"
    )
    company: str | None = Field(
        default=None, description="Organization or employer name"
    )
    employment_type: str | None = Field(
        default=None, description="Employment type (e.g. Internship, Full-time)"
    )
    location: str | None = Field(
        default=None, description="Workplace location or work mode (e.g. Remote, City, State)"
    )
    start_date: str | None = Field(
        default=None, description="Start date (month/year or year)"
    )
    end_date: str | None = Field(
        default=None, description="End date (month/year, year, or Present)"
    )
    description: str | None = Field(
        default=None, description="Summary of responsibilities and achievements"
    )
    technologies: list[str] = Field(
        default_factory=list, description="Technologies and tools used in this role"
    )


class ProjectEntry(BaseModel):
    """Personal, academic, or professional project entry."""

    project_name: str | None = Field(
        default=None, description="Name or title of the project"
    )
    description: str | None = Field(
        default=None, description="Key details, objective, and impact of the project"
    )
    technologies: list[str] = Field(
        default_factory=list, description="Technologies and libraries utilized"
    )
    project_url: str | None = Field(
        default=None, description="Link to source code repository or live demo"
    )


class CertificationEntry(BaseModel):
    """Professional license, certification, or accredited course."""

    certification_name: str | None = Field(
        default=None, description="Title of the certification or course"
    )
    issuing_organization: str | None = Field(
        default=None, description="Issuing body, company, or platform"
    )
    issue_date: str | None = Field(
        default=None, description="Date or year of completion / issuance"
    )
    credential_url: str | None = Field(
        default=None, description="Verification or credential link"
    )


class AchievementEntry(BaseModel):
    """Awards, honors, coding milestones, and competition achievements."""

    title: str = Field(
        description="Title or description of the achievement"
    )
    category: str | None = Field(
        default=None,
        description="Classification (e.g. Award, Coding Milestone, Competition)",
    )
    organization: str | None = Field(
        default=None,
        description="Associated organization, platform, or institution",
    )


class CandidateProfile(BaseModel):
    """Consolidated candidate profile extracted from a resume."""

    personal_information: PersonalInformation = Field(
        default_factory=PersonalInformation,
        description="Candidate personal and contact details",
    )
    professional_summary: str | None = Field(
        default=None,
        description="Professional summary or career objective statement",
    )
    technical_skills: TechnicalSkills = Field(
        default_factory=TechnicalSkills,
        description="Structured categorized technical competencies",
    )
    education: list[EducationEntry] = Field(
        default_factory=list,
        description="Educational qualifications in reverse chronological order",
    )
    experience: list[ExperienceEntry] = Field(
        default_factory=list,
        description="Work and internship history",
    )
    projects: list[ProjectEntry] = Field(
        default_factory=list,
        description="Portfolio and notable projects",
    )
    certifications: list[CertificationEntry] = Field(
        default_factory=list,
        description="Professional certifications and accredited programs",
    )
    achievements: list[AchievementEntry] = Field(
        default_factory=list,
        description="Awards, competitive milestones, and competition achievements",
    )


class ResumeParseResponse(BaseModel):
    """API response model for POST /api/v1/resumes/{file_id}/parse."""

    success: bool = True
    file_id: str = Field(
        description="Unique 32-character hexadecimal file identifier"
    )
    candidate: CandidateProfile = Field(
        description="Complete structured candidate profile"
    )
