"""
Curated Role Benchmark Catalog for Skill Gap Analysis.
Provides standardized, maintainable skill expectations across key software engineering domains.
Benchmark data is cleanly separated from matching algorithms to allow future custom benchmarks.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class BenchmarkSkill(BaseModel):
    """Individual skill definition within a role benchmark."""

    skill_name: str = Field(description="Canonical skill name matching the platform taxonomy")
    category: str = Field(description="Technical skill category (one of 10 supported domains)")
    importance: str = Field(default="required", description="'required' or 'preferred'")
    weight: float = Field(default=1.0, description="Numerical weight for scoring calculations")


class RoleBenchmark(BaseModel):
    """Complete role benchmark defining required and preferred skills for a target career role."""

    role_id: str = Field(description="Stable URL-friendly identifier, e.g. 'sde', 'backend_developer'")
    title: str = Field(description="Human-readable title, e.g. 'Software Development Engineer (SDE)'")
    description: str = Field(description="Objective overview of baseline technical expectations")
    domain: str = Field(description="Industry domain, e.g. 'Software Engineering', 'Data & Analytics', 'AI / ML'")
    version: str = Field(default="1.0.0", description="Benchmark definition version")
    required_skills: List[BenchmarkSkill] = Field(default_factory=list)
    preferred_skills: List[BenchmarkSkill] = Field(default_factory=list)
    is_custom: bool = Field(default=False, description="Whether this is a user-defined custom benchmark")

    @property
    def total_required(self) -> int:
        return len(self.required_skills)

    @property
    def total_preferred(self) -> int:
        return len(self.preferred_skills)


# =============================================================================
# Curated Standard Role Benchmarks (Initial 8 Supported Roles)
# =============================================================================

ROLE_CATALOG: Dict[str, RoleBenchmark] = {
    # 1. Software Development Engineer (SDE)
    "sde": RoleBenchmark(
        role_id="sde",
        title="Software Development Engineer (SDE)",
        description="Core software engineering role focusing on algorithmic problem solving, system design, scalable REST APIs, and robust data structures.",
        domain="Software Engineering",
        version="1.0.0",
        required_skills=[
            BenchmarkSkill(skill_name="Python", category="programming_languages", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="Java", category="programming_languages", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="Data Structures", category="other", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="Algorithms", category="other", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="SQL", category="databases", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="Git", category="tools", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="REST API", category="backend", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="System Design", category="other", importance="required", weight=1.0),
        ],
        preferred_skills=[
            BenchmarkSkill(skill_name="Docker", category="cloud_devops", importance="preferred", weight=0.5),
            BenchmarkSkill(skill_name="Redis", category="databases", importance="preferred", weight=0.5),
            BenchmarkSkill(skill_name="CI/CD", category="cloud_devops", importance="preferred", weight=0.5),
            BenchmarkSkill(skill_name="Linux", category="tools", importance="preferred", weight=0.5),
            BenchmarkSkill(skill_name="PostgreSQL", category="databases", importance="preferred", weight=0.5),
        ],
    ),

    # 2. Frontend Developer
    "frontend_developer": RoleBenchmark(
        role_id="frontend_developer",
        title="Frontend Developer",
        description="Specializes in client-side web applications, responsive user interfaces, component architectures, and web performance.",
        domain="Web Development",
        version="1.0.0",
        required_skills=[
            BenchmarkSkill(skill_name="JavaScript", category="programming_languages", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="TypeScript", category="programming_languages", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="React", category="frontend", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="HTML5", category="frontend", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="CSS3", category="frontend", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="Tailwind CSS", category="frontend", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="Git", category="tools", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="REST API", category="backend", importance="required", weight=1.0),
        ],
        preferred_skills=[
            BenchmarkSkill(skill_name="Next.js", category="frontend", importance="preferred", weight=0.5),
            BenchmarkSkill(skill_name="Redux", category="frontend", importance="preferred", weight=0.5),
            BenchmarkSkill(skill_name="Vite", category="frontend", importance="preferred", weight=0.5),
            BenchmarkSkill(skill_name="Responsive Design", category="frontend", importance="preferred", weight=0.5),
            BenchmarkSkill(skill_name="GraphQL", category="backend", importance="preferred", weight=0.5),
        ],
    ),

    # 3. Backend Developer
    "backend_developer": RoleBenchmark(
        role_id="backend_developer",
        title="Backend Developer",
        description="Focuses on server-side architecture, relational and NoSQL database modeling, REST/GraphQL microservices, and secure API integrations.",
        domain="Web Development",
        version="1.0.0",
        required_skills=[
            BenchmarkSkill(skill_name="Python", category="programming_languages", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="SQL", category="databases", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="PostgreSQL", category="databases", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="FastAPI", category="backend", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="REST API", category="backend", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="Git", category="tools", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="Docker", category="cloud_devops", importance="required", weight=1.0),
        ],
        preferred_skills=[
            BenchmarkSkill(skill_name="Redis", category="databases", importance="preferred", weight=0.5),
            BenchmarkSkill(skill_name="Django", category="backend", importance="preferred", weight=0.5),
            BenchmarkSkill(skill_name="Microservices", category="other", importance="preferred", weight=0.5),
            BenchmarkSkill(skill_name="AWS", category="cloud_devops", importance="preferred", weight=0.5),
            BenchmarkSkill(skill_name="CI/CD", category="cloud_devops", importance="preferred", weight=0.5),
        ],
    ),

    # 4. Full Stack Developer
    "full_stack_developer": RoleBenchmark(
        role_id="full_stack_developer",
        title="Full Stack Developer",
        description="Bridges client-side UI and server-side services with end-to-end full stack development, database integration, and deployment.",
        domain="Web Development",
        version="1.0.0",
        required_skills=[
            BenchmarkSkill(skill_name="JavaScript", category="programming_languages", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="React", category="frontend", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="Node.js", category="backend", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="SQL", category="databases", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="HTML5", category="frontend", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="CSS3", category="frontend", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="REST API", category="backend", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="Git", category="tools", importance="required", weight=1.0),
        ],
        preferred_skills=[
            BenchmarkSkill(skill_name="TypeScript", category="programming_languages", importance="preferred", weight=0.5),
            BenchmarkSkill(skill_name="PostgreSQL", category="databases", importance="preferred", weight=0.5),
            BenchmarkSkill(skill_name="Docker", category="cloud_devops", importance="preferred", weight=0.5),
            BenchmarkSkill(skill_name="Tailwind CSS", category="frontend", importance="preferred", weight=0.5),
            BenchmarkSkill(skill_name="Next.js", category="frontend", importance="preferred", weight=0.5),
        ],
    ),

    # 5. Data Analyst
    "data_analyst": RoleBenchmark(
        role_id="data_analyst",
        title="Data Analyst",
        description="Focuses on querying structured datasets, exploratory data analysis, KPI reporting, statistical evaluation, and interactive executive dashboards.",
        domain="Data & Analytics",
        version="1.0.0",
        required_skills=[
            BenchmarkSkill(skill_name="SQL", category="databases", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="Python", category="programming_languages", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="Excel", category="data_analytics", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="Power BI", category="data_analytics", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="Data Analytics", category="data_analytics", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="Data Visualization", category="data_analytics", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="Pandas", category="data_analytics", importance="required", weight=1.0),
        ],
        preferred_skills=[
            BenchmarkSkill(skill_name="NumPy", category="data_analytics", importance="preferred", weight=0.5),
            BenchmarkSkill(skill_name="Tableau", category="data_analytics", importance="preferred", weight=0.5),
            BenchmarkSkill(skill_name="Data Cleaning", category="data_analytics", importance="preferred", weight=0.5),
            BenchmarkSkill(skill_name="Statistics", category="other", importance="preferred", weight=0.5),
            BenchmarkSkill(skill_name="Git", category="tools", importance="preferred", weight=0.5),
        ],
    ),

    # 6. Data Scientist
    "data_scientist": RoleBenchmark(
        role_id="data_scientist",
        title="Data Scientist",
        description="Combines advanced statistical analysis, machine learning models, predictive forecasting, and scientific Python programming to derive actionable insights.",
        domain="Data & Analytics",
        version="1.0.0",
        required_skills=[
            BenchmarkSkill(skill_name="Python", category="programming_languages", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="SQL", category="databases", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="Machine Learning", category="machine_learning", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="Pandas", category="data_analytics", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="NumPy", category="data_analytics", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="Scikit-Learn", category="machine_learning", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="Data Visualization", category="data_analytics", importance="required", weight=1.0),
        ],
        preferred_skills=[
            BenchmarkSkill(skill_name="Deep Learning", category="deep_learning", importance="preferred", weight=0.5),
            BenchmarkSkill(skill_name="PyTorch", category="deep_learning", importance="preferred", weight=0.5),
            BenchmarkSkill(skill_name="TensorFlow", category="deep_learning", importance="preferred", weight=0.5),
            BenchmarkSkill(skill_name="Git", category="tools", importance="preferred", weight=0.5),
            BenchmarkSkill(skill_name="Docker", category="cloud_devops", importance="preferred", weight=0.5),
        ],
    ),

    # 7. Machine Learning Engineer
    "machine_learning_engineer": RoleBenchmark(
        role_id="machine_learning_engineer",
        title="Machine Learning Engineer",
        description="Designs, trains, and operationalizes machine learning and deep learning models for production systems, MLOps, and model serving.",
        domain="AI / ML",
        version="1.0.0",
        required_skills=[
            BenchmarkSkill(skill_name="Python", category="programming_languages", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="Machine Learning", category="machine_learning", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="Deep Learning", category="deep_learning", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="PyTorch", category="deep_learning", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="TensorFlow", category="deep_learning", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="Scikit-Learn", category="machine_learning", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="Docker", category="cloud_devops", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="Git", category="tools", importance="required", weight=1.0),
        ],
        preferred_skills=[
            BenchmarkSkill(skill_name="FastAPI", category="backend", importance="preferred", weight=0.5),
            BenchmarkSkill(skill_name="Kubernetes", category="cloud_devops", importance="preferred", weight=0.5),
            BenchmarkSkill(skill_name="SQL", category="databases", importance="preferred", weight=0.5),
            BenchmarkSkill(skill_name="Pandas", category="data_analytics", importance="preferred", weight=0.5),
            BenchmarkSkill(skill_name="Cloud Infrastructure", category="cloud_devops", importance="preferred", weight=0.5),
        ],
    ),

    # 8. Python Developer
    "python_developer": RoleBenchmark(
        role_id="python_developer",
        title="Python Developer",
        description="Specializes in idiomatic Python development, backend web frameworks (FastAPI/Django), automated scripting, database persistence, and API engineering.",
        domain="Software Engineering",
        version="1.0.0",
        required_skills=[
            BenchmarkSkill(skill_name="Python", category="programming_languages", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="FastAPI", category="backend", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="SQL", category="databases", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="PostgreSQL", category="databases", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="REST API", category="backend", importance="required", weight=1.0),
            BenchmarkSkill(skill_name="Git", category="tools", importance="required", weight=1.0),
        ],
        preferred_skills=[
            BenchmarkSkill(skill_name="Django", category="backend", importance="preferred", weight=0.5),
            BenchmarkSkill(skill_name="Flask", category="backend", importance="preferred", weight=0.5),
            BenchmarkSkill(skill_name="Docker", category="cloud_devops", importance="preferred", weight=0.5),
            BenchmarkSkill(skill_name="Redis", category="databases", importance="preferred", weight=0.5),
            BenchmarkSkill(skill_name="Linux", category="tools", importance="preferred", weight=0.5),
        ],
    ),
}


def get_role_benchmarks() -> List[RoleBenchmark]:
    """Retrieve all available standard role benchmarks."""
    return list(ROLE_CATALOG.values())


def get_role_benchmark(role_id: str) -> Optional[RoleBenchmark]:
    """Retrieve a specific role benchmark by ID (case-insensitive)."""
    if not role_id:
        return None
    return ROLE_CATALOG.get(role_id.strip().lower())


def get_supported_role_ids() -> List[str]:
    """Return a list of all supported role identifiers."""
    return list(ROLE_CATALOG.keys())

