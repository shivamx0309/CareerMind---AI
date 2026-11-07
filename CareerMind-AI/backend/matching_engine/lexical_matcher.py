"""
Lexical Similarity Engine for CareerMind AI (Phase 5.4).

Computes deterministic lexical cosine similarity between candidate resume text
and target job description using n-gram term frequencies and NumPy.

Architectural Notice:
This module measures lexical surface similarity (word and phrase overlap),
NOT true semantic embedding similarity. It serves as a transparent baseline
and can be complemented or extended by local Sentence Transformers in the future.
"""

import re
import math
from collections import Counter
import numpy as np


STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "did", "do", "does", "doing", "don't", "down", "during", "each", "few", "for",
    "from", "further", "had", "has", "have", "having", "he", "her", "here", "hers",
    "herself", "him", "himself", "his", "how", "i", "if", "in", "into", "is",
    "isn't", "it", "its", "itself", "let's", "me", "more", "most", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "she", "should",
    "so", "some", "such", "than", "that", "the", "their", "theirs", "them",
    "themselves", "then", "there", "these", "they", "this", "those", "through",
    "to", "too", "under", "until", "up", "very", "was", "we", "were", "what",
    "when", "where", "which", "while", "who", "whom", "why", "with", "would",
    "you", "your", "yours", "yourself", "yourselves", "will", "shall", "may",
    "must", "can", "work", "job", "candidate", "role", "team", "years", "looking",
}


def _tokenize_ngrams(text: str) -> list[str]:
    """Tokenize text into unigrams and bigrams, excluding common stopwords."""
    if not text:
        return []

    words = re.findall(r"\b[a-zA-Z0-9+#.-]+\b", text.lower())
    clean_words = [w for w in words if w not in STOPWORDS and len(w) > 1]

    tokens: list[str] = list(clean_words)

    # Bigrams for multi-word domain phrases (e.g. "rest api", "full stack", "cloud computing")
    for i in range(len(clean_words) - 1):
        bigram = f"{clean_words[i]} {clean_words[i+1]}"
        tokens.append(bigram)

    return tokens


def calculate_lexical_similarity(
    candidate_text: str,
    jd_text: str,
) -> tuple[float, list[str]]:
    """
    Compute lexical cosine similarity between candidate text and job description text.

    Args:
        candidate_text: Full aggregated text from the candidate profile.
        jd_text: Raw job description text.

    Returns:
        tuple containing:
        - similarity_score: float in [0.0, 100.0]
        - top_overlapping_terms: list[str] of top shared n-grams
    """
    cand_tokens = _tokenize_ngrams(candidate_text)
    jd_tokens = _tokenize_ngrams(jd_text)

    if not cand_tokens or not jd_tokens:
        return 0.0, []

    cand_counts = Counter(cand_tokens)
    jd_counts = Counter(jd_tokens)

    # Common vocabulary (sorted for deterministic repeatability)
    all_vocab = sorted(list(set(cand_counts.keys()) | set(jd_counts.keys())))
    if not all_vocab:
        return 0.0, []

    # Vector construction with term frequency and sublinear scaling
    v_cand = np.array([1.0 + math.log(cand_counts[t]) if cand_counts[t] > 0 else 0.0 for t in all_vocab], dtype=np.float64)
    v_jd = np.array([1.0 + math.log(jd_counts[t]) if jd_counts[t] > 0 else 0.0 for t in all_vocab], dtype=np.float64)

    norm_cand = np.linalg.norm(v_cand)
    norm_jd = np.linalg.norm(v_jd)

    if norm_cand == 0.0 or norm_jd == 0.0:
        return 0.0, []

    # Cosine similarity
    cosine_sim = float(np.dot(v_cand, v_jd) / (norm_cand * norm_jd))
    cosine_sim = max(0.0, min(1.0, cosine_sim))

    # Identify top shared lexical terms
    overlap_scores = []
    for idx, token in enumerate(all_vocab):
        prod = v_cand[idx] * v_jd[idx]
        if prod > 0.0:
            overlap_scores.append((token, prod))

    overlap_scores.sort(key=lambda x: (-x[1], x[0]))
    top_terms = [t for t, _ in overlap_scores[:10]]

    # Scale to 0 - 100
    score = round(cosine_sim * 100.0, 1)
    return score, top_terms

