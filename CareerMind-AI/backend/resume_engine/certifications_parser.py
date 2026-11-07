"""
Certifications and achievements parser for resume text.

Distinguishes:
1. Accredited certifications, job simulations, and educational programs.
2. Honors, awards, competition wins, and competitive coding milestones.
"""

import re
from schemas.candidate_schema import CertificationEntry, AchievementEntry


# Recognized certification issuing organizations
ISSUING_ORGANIZATIONS = [
    ("Deloitte", r"\bDeloitte\b"),
    ("Accenture", r"\bAccenture\b"),
    ("Tata", r"\bTata\b"),
    ("Apna College", r"\bApna\s+College\b"),
    ("Amazon Web Services", r"\b(?:Amazon\s+Web\s+Services|AWS)\b"),
    ("Google", r"\bGoogle(?:\s+Cloud)?\b"),
    ("Microsoft", r"\bMicrosoft(?:\s+Azure)?\b"),
    ("Meta", r"\bMeta\b"),
    ("IBM", r"\bIBM\b"),
    ("Oracle", r"\bOracle\b"),
    ("Cisco", r"\bCisco\b"),
    ("Coursera", r"\bCoursera\b"),
    ("edX", r"\bedX\b"),
    ("Udacity", r"\bUdacity\b"),
    ("Udemy", r"\bUdemy\b"),
    ("HackerRank", r"\bHackerRank\b"),
    ("LeetCode", r"\bLeetCode\b"),
    ("CodeChef", r"\bCodeChef\b"),
    ("Kaggle", r"\bKaggle\b"),
    ("DeepLearning.AI", r"\bDeepLearning\.AI\b"),
    ("CompTIA", r"\bCompTIA\b"),
]

# Year / date pattern
DATE_REGEX = re.compile(
    r"\b((?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+)?(?:19|20)\d{2})\b",
    re.IGNORECASE,
)

# Inline URL regex
URL_REGEX = re.compile(
    r"https?://(?:www\.)?[a-zA-Z0-9_-]+(?:\.[a-zA-Z0-9_-]+)+(?:/[^\s]*)?",
    re.IGNORECASE,
)


def extract_issuing_organization(text: str) -> str | None:
    """Identify the issuing body or organization from text."""
    for canonical_name, pattern in ISSUING_ORGANIZATIONS:
        if re.search(pattern, text, re.IGNORECASE):
            return canonical_name
    return None


def parse_certification_entries(
    certification_lines: list[str],
    links: list[str] | None = None,
) -> list[CertificationEntry]:
    """
    Parse accredited certifications, professional licenses, and job simulations.
    """
    if not certification_lines:
        return []

    entries: list[CertificationEntry] = []

    for line in certification_lines:
        cleaned = re.sub(r"^[•\-\*\s]+", "", line).strip()
        # Skip empty lines, page numbers, and short noise
        if not cleaned or re.match(r"^\d+$", cleaned) or len(cleaned) < 3:
            continue

        # Extract URL if present
        credential_url = None
        url_match = URL_REGEX.search(cleaned)
        if url_match:
            credential_url = url_match.group(0).rstrip(".,;:)>]")
            cleaned = URL_REGEX.sub("", cleaned).strip()

        # Extract issue date
        issue_date = None
        date_match = DATE_REGEX.search(cleaned)
        if date_match:
            issue_date = date_match.group(1).strip()
            cleaned = re.sub(r"\(\s*" + re.escape(issue_date) + r"\s*\)", "", cleaned).strip()

        # Split format "Course / Cert Name – Issuing Organization"
        issuing_org = None
        cert_name = cleaned
        for sep in ("—", "–", " - "):
            if sep in cleaned:
                parts = cleaned.split(sep, 1)
                p_org = extract_issuing_organization(parts[1])
                if p_org or any(kw in parts[1].lower() for kw in ("college", "university", "academy", "institute")):
                    cert_name = parts[0].strip()
                    issuing_org = p_org or parts[1].strip()
                    break

        if not issuing_org:
            issuing_org = extract_issuing_organization(cleaned)

        # Clean "Completed" or "Earned" prefix
        cleaned_name = re.sub(r"^(?:completed|earned|achieved|certified\s+in)\s+", "", cert_name, flags=re.IGNORECASE).strip()
        final_name = cleaned_name.rstrip(" -—–|:.")

        if final_name:
            entries.append(
                CertificationEntry(
                    certification_name=final_name,
                    issuing_organization=issuing_org,
                    issue_date=issue_date,
                    credential_url=credential_url,
                )
            )

    return entries


def parse_achievement_entries(
    achievement_lines: list[str],
) -> list[AchievementEntry]:
    """
    Parse honors, awards, competitive coding milestones, and competition achievements.
    """
    if not achievement_lines:
        return []

    entries: list[AchievementEntry] = []

    for line in achievement_lines:
        cleaned = re.sub(r"^[•\-\*\s]+", "", line).strip()
        if not cleaned or re.match(r"^\d+$", cleaned) or len(cleaned) < 3:
            continue

        category = None
        org = extract_issuing_organization(cleaned)

        # Award / Honor
        if re.search(r"\b(?:badge\s+of\s+honou?r|award|honou?r|medal|scholarship|trophy|recognized|recognition)\b", cleaned, re.I):
            category = "Award / Recognition"
            # Check for employer or organization in the line: e.g. "from Humppl"
            org_match = re.search(r"\b(?:from|by|at)\s+([A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)*)", cleaned)
            if org_match and not org:
                org = org_match.group(1).strip()

        # Competition / Contest
        elif re.search(r"\b(?:place|winner|runner-up|hackathon|competition|contest|championship|ranked|top\s+\d+)\b", cleaned, re.I):
            category = "Competition"

        # Coding Milestone
        elif re.search(r"\b(?:solved\s+\d+|problems|leetcode|hackerrank|codechef|codeforces|streak)\b", cleaned, re.I):
            category = "Coding Milestone"

        else:
            category = "Milestone"

        entries.append(
            AchievementEntry(
                title=cleaned,
                category=category,
                organization=org,
            )
        )

    return entries
