"""
Deterministic & Explainable Answer Evaluation Engine for AI Mock Interview Simulator.
Evaluates candidate responses against curated question rubrics, expected concepts,
relevance anchors, and structural clarity without relying on external paid LLM APIs.
"""

import re
from typing import List, Dict, Any, Set, Tuple
from pydantic import BaseModel, Field


class EvaluationResult(BaseModel):
    """Structured evaluation output for a submitted interview answer."""

    overall_score: float = Field(ge=0.0, le=100.0, description="Weighted composite score")
    relevance_score: float = Field(ge=0.0, le=100.0, description="Relevance to question domain")
    concept_coverage_score: float = Field(ge=0.0, le=100.0, description="Percentage of expected concepts covered")
    completeness_score: float = Field(ge=0.0, le=100.0, description="Substantive depth without penalizing conciseness")
    structure_score: float = Field(ge=0.0, le=100.0, description="Structural organization and clarity")
    identified_concepts: List[str] = Field(default_factory=list)
    missing_concepts: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    improvement_suggestions: List[str] = Field(default_factory=list)
    evaluator_method: str = "deterministic_rubric_v1"
    feedback_rationale: str


# Common stop words to exclude when analyzing lexical relevance
STOP_WORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't",
    "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he",
    "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's",
    "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or",
    "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll",
    "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them",
    "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this",
    "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're",
    "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who",
    "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're",
    "you've", "your", "yours", "yourself", "yourselves"
}

# Structural markers for clarity scoring
STRUCTURAL_CONNECTORS = [
    "because", "therefore", "for example", "for instance", "in contrast", "on the other hand",
    "however", "furthermore", "specifically", "as a result", "whereas", "firstly", "secondly",
    "in summary", "to summarize", "consequently", "situation", "task", "action", "result"
]


def tokenize_text(text: str) -> List[str]:
    """Extract lowercased alphanumeric tokens from text."""
    if not text:
        return []
    return re.findall(r"\b[a-zA-Z0-9_\-\.\#\+]+\b", text.lower())


def check_concept_presence(concept: str, text_lower: str, token_set: Set[str]) -> bool:
    """
    Check if an expected concept is present in the text using:
    1. Exact phrase substring match
    2. Token boundary match
    3. Multi-word individual token match
    """
    concept_lower = concept.lower().strip()
    if not concept_lower:
        return False

    # 1. Exact substring match
    if concept_lower in text_lower:
        return True

    # 2. Multi-word concept token match (e.g. "Global Interpreter Lock" -> "gil" or all words present)
    words = concept_lower.split()
    if len(words) > 1:
        # Check if acronym is in tokens (e.g. "gil", "acid", "vdom")
        acronym = "".join(w[0] for w in words if w)
        if acronym in token_set:
            return True

        # Check if all key substantive words of the concept appear in text
        key_words = [w for w in words if w not in STOP_WORDS]
        if key_words and all(kw in text_lower for kw in key_words):
            return True

    # 3. Lemmatization / Stemming variations (e.g. "indexing" -> "index", "threads" -> "thread")
    if concept_lower.endswith("ing") and concept_lower[:-3] in text_lower:
        return True
    if concept_lower.endswith("s") and concept_lower[:-1] in text_lower:
        return True
    if concept_lower.endswith("ed") and concept_lower[:-2] in text_lower:
        return True

    return False


def evaluate_answer(
    answer_text: str,
    question_text: str,
    expected_concepts: List[str],
    suggested_answer_points: List[str],
    evaluation_rubric: Dict[str, Any],
    interview_type: str = "technical",
    difficulty: str = "intermediate",
) -> EvaluationResult:
    """
    Evaluate a candidate's answer deterministically against question criteria.

    Weights:
        - Concept Coverage: 40%
        - Relevance: 25%
        - Completeness: 20%
        - Structure & Clarity: 15%
    """
    cleaned_answer = (answer_text or "").strip()

    # 1. Edge Case: Empty Answer
    if not cleaned_answer:
        return EvaluationResult(
            overall_score=0.0,
            relevance_score=0.0,
            concept_coverage_score=0.0,
            completeness_score=0.0,
            structure_score=0.0,
            identified_concepts=[],
            missing_concepts=list(expected_concepts),
            strengths=[],
            improvement_suggestions=[
                "No answer was provided. Attempt to answer using relevant technical concepts, definitions, or the STAR format."
            ],
            evaluator_method="deterministic_rubric_v1",
            feedback_rationale="The response was completely blank. 0 points awarded across all evaluation criteria.",
        )

    tokens = tokenize_text(cleaned_answer)
    word_count = len(tokens)
    token_set = set(tokens)
    text_lower = cleaned_answer.lower()

    # 2. Edge Case: Extremely Short Answer (< 4 words)
    if word_count < 4:
        return EvaluationResult(
            overall_score=10.0,
            relevance_score=15.0,
            concept_coverage_score=5.0,
            completeness_score=5.0,
            structure_score=15.0,
            identified_concepts=[],
            missing_concepts=list(expected_concepts),
            strengths=["Submitted a brief response."],
            improvement_suggestions=[
                "Expand on your answer. Interviewers look for explanations of mechanisms, trade-offs, and examples rather than single-phrase answers."
            ],
            evaluator_method="deterministic_rubric_v1",
            feedback_rationale="The answer is too brief to demonstrate technical competency. Elaborate on the core concepts to receive full credit.",
        )

    # =========================================================================
    # A. Concept Coverage Evaluation (Weight: 40%)
    # =========================================================================
    identified: List[str] = []
    missing: List[str] = []

    for concept in expected_concepts:
        if check_concept_presence(concept, text_lower, token_set):
            identified.append(concept)
        else:
            missing.append(concept)

    if expected_concepts:
        concept_coverage_ratio = len(identified) / len(expected_concepts)
        concept_coverage_score = round(concept_coverage_ratio * 100.0, 1)
    else:
        concept_coverage_score = 75.0  # neutral fallback if question has no explicit concepts

    # =========================================================================
    # B. Relevance Evaluation (Weight: 25%)
    # =========================================================================
    q_tokens = [t for t in tokenize_text(question_text) if t not in STOP_WORDS]
    rubric_keywords = [k.lower() for k in evaluation_rubric.get("required_keywords", [])]

    # Combine question anchors and rubric keywords
    anchor_terms = set(q_tokens + rubric_keywords)
    matched_anchors = [a for a in anchor_terms if a in text_lower or a in token_set]

    if anchor_terms:
        relevance_ratio = len(matched_anchors) / len(anchor_terms)
        # Scale generously: hitting 40% of anchors indicates high topical relevance
        relevance_score = min(100.0, round((relevance_ratio / 0.40) * 100.0, 1))
    else:
        relevance_score = 80.0

    # Ensure minimum threshold if at least one expected concept or keyword is present
    if identified and relevance_score < 40.0:
        relevance_score = 60.0

    # =========================================================================
    # C. Completeness Evaluation (Weight: 20%)
    # =========================================================================
    # Concise answers with high concept coverage are NOT penalized.
    # We calibrate target word counts based on difficulty:
    # Beginner: 30-100 words, Intermediate: 50-180 words, Advanced: 70-250 words.
    min_words = 25 if difficulty == "beginner" else (40 if difficulty == "intermediate" else 55)

    if word_count >= min_words:
        # If candidate covered >= 60% of concepts, grant full completeness
        if concept_coverage_score >= 60.0:
            completeness_score = 100.0
        else:
            completeness_score = max(50.0, min(95.0, concept_coverage_score + 25.0))
    else:
        # Partial completeness proportional to word count and concept hits
        completeness_score = round(min(80.0, (word_count / min_words) * 70.0 + (len(identified) * 10)), 1)

    # =========================================================================
    # D. Structure and Clarity Evaluation (Weight: 15%)
    # =========================================================================
    structure_points = 50.0  # base baseline for a coherent paragraph

    # Check for formatting (paragraphs, bullet points, numbered lists)
    has_bullets = bool(re.search(r"(\n\s*[-*•]|\n\s*\d+\.)", answer_text))
    has_multiple_paragraphs = len(re.split(r"\n\s*\n", answer_text)) > 1

    if has_bullets or has_multiple_paragraphs:
        structure_points += 20.0

    # Check for logical and causal transition phrases
    matched_connectors = [c for c in STRUCTURAL_CONNECTORS if c in text_lower]
    if len(matched_connectors) >= 2:
        structure_points += 20.0
    elif len(matched_connectors) == 1:
        structure_points += 10.0

    # For behavioral interviews: check for STAR elements
    if interview_type == "behavioral":
        star_terms = ["situation", "task", "action", "result", "outcome", "learned"]
        star_hits = [st for st in star_terms if st in text_lower]
        if len(star_hits) >= 3:
            structure_points += 15.0

    structure_score = min(100.0, round(structure_points, 1))

    # =========================================================================
    # E. Overall Weighted Score Calculation
    # =========================================================================
    # Formula: 0.40 * Concept + 0.25 * Relevance + 0.20 * Completeness + 0.15 * Structure
    overall = (
        0.40 * concept_coverage_score
        + 0.25 * relevance_score
        + 0.20 * completeness_score
        + 0.15 * structure_score
    )
    overall_score = round(min(100.0, max(0.0, overall)), 1)

    # =========================================================================
    # F. Feedback Generation (Strengths & Improvements)
    # =========================================================================
    strengths: List[str] = []
    improvement_suggestions: List[str] = []

    if identified:
        strengths.append(f"Correctly identified and explained key concepts: {', '.join(identified[:4])}.")
    if structure_score >= 80.0:
        strengths.append("Answer is well-structured with clear transitions and logical progression.")
    if relevance_score >= 80.0:
        strengths.append("Directly addressed the core question without straying into unrelated topics.")
    if completeness_score >= 85.0 and word_count >= min_words:
        strengths.append("Provided substantive technical depth and sufficient explanatory detail.")

    if not strengths:
        strengths.append("Addressed the general topic.")

    if missing:
        improvement_suggestions.append(
            f"Incorporate these missing concepts to strengthen your answer: {', '.join(missing[:4])}."
        )
    if structure_score < 70.0:
        if interview_type == "behavioral":
            improvement_suggestions.append("Structure your response using the STAR method: Situation, Task, Action, and Result.")
        else:
            improvement_suggestions.append("Use bullet points or transitional phrasing (e.g. 'for example', 'in contrast') to improve clarity.")
    if word_count < min_words:
        improvement_suggestions.append(f"Elaborate further on architectural trade-offs or implementation nuances (target at least {min_words} words).")

    if not improvement_suggestions:
        improvement_suggestions.append("Comprehensive response. Continue applying this level of structured precision.")

    feedback_rationale = (
        f"Score {overall_score}/100 calculated using deterministic rubric: "
        f"Concept Coverage ({concept_coverage_score}%, weight 40%), "
        f"Relevance ({relevance_score}%, weight 25%), "
        f"Completeness ({completeness_score}%, weight 20%), "
        f"Structure ({structure_score}%, weight 15%). "
        f"{len(identified)} of {len(expected_concepts)} target concepts covered."
    )

    return EvaluationResult(
        overall_score=overall_score,
        relevance_score=relevance_score,
        concept_coverage_score=concept_coverage_score,
        completeness_score=completeness_score,
        structure_score=structure_score,
        identified_concepts=identified,
        missing_concepts=missing,
        strengths=strengths,
        improvement_suggestions=improvement_suggestions,
        evaluator_method="deterministic_rubric_v1",
        feedback_rationale=feedback_rationale,
    )

