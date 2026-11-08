"""
Database entity registry exporting all SQLAlchemy models.
"""

from database.models.career_profile import CareerProfile
from database.models.career_goal import CareerGoal
from database.models.learning_preference import LearningPreference
from database.models.resume_record import ResumeRecord
from database.models.resume_profile import ResumeProfile
from database.models.resume_skill import ResumeSkill
from database.models.resume_education import ResumeEducation
from database.models.resume_experience import ResumeExperience
from database.models.resume_project import ResumeProject
from database.models.resume_certification import ResumeCertification

__all__ = [
    "CareerProfile",
    "CareerGoal",
    "LearningPreference",
    "ResumeRecord",
    "ResumeProfile",
    "ResumeSkill",
    "ResumeEducation",
    "ResumeExperience",
    "ResumeProject",
    "ResumeCertification",
]
