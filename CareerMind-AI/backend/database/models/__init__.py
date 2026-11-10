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
from database.models.skill_gap_report import SkillGapReport
from database.models.learning_roadmap import LearningRoadmap
from database.models.roadmap_skill import RoadmapSkill
from database.models.roadmap_topic import RoadmapTopic
from database.models.learning_resource import LearningResource
from database.models.roadmap_milestone import RoadmapMilestone
from database.models.interview_session import InterviewSession
from database.models.interview_session_question import InterviewSessionQuestion
from database.models.interview_answer import InterviewAnswer
from database.models.interview_evaluation import InterviewEvaluation
from database.models.interview_report import InterviewReport

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
    "SkillGapReport",
    "LearningRoadmap",
    "RoadmapSkill",
    "RoadmapTopic",
    "LearningResource",
    "RoadmapMilestone",
    "InterviewSession",
    "InterviewSessionQuestion",
    "InterviewAnswer",
    "InterviewEvaluation",
    "InterviewReport",
]
