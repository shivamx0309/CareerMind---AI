"""Package initialization for matching_engine."""

from matching_engine.jd_parser import parse_job_description
from matching_engine.skill_matcher import (
    match_candidate_skills,
    extract_candidate_skill_evidence,
)
from matching_engine.experience_matcher import match_candidate_experience
from matching_engine.education_matcher import match_candidate_education
from matching_engine.lexical_matcher import calculate_lexical_similarity
from matching_engine.score_calculator import calculate_match_score, DEFAULT_WEIGHTS
from matching_engine.recommendation_engine import generate_recommendations
from matching_engine.matching_service import execute_job_matching, count_unique_candidate_skills

__all__ = [
    "parse_job_description",
    "match_candidate_skills",
    "extract_candidate_skill_evidence",
    "match_candidate_experience",
    "match_candidate_education",
    "calculate_lexical_similarity",
    "calculate_match_score",
    "DEFAULT_WEIGHTS",
    "generate_recommendations",
    "execute_job_matching",
    "count_unique_candidate_skills",
]
