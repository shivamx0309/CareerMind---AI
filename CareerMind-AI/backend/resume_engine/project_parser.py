"""
Project information parser for resume text.

Extracts project title, description, technologies used, and repository/live URLs.
Cleans out standalone hyperlink labels (e.g. 'Live Demo', 'GitHub', 'Demo') from descriptions.
Supports single or multiple project entries.
"""

import re
from schemas.candidate_schema import ProjectEntry
from resume_engine.skills_parser import SKILL_TAXONOMY, resolve_skill_alias


# Regex for inline URLs
URL_REGEX = re.compile(
    r"https?://(?:www\.)?[a-zA-Z0-9_-]+(?:\.[a-zA-Z0-9_-]+)+(?:/[^\s]*)?",
    re.IGNORECASE,
)

# Standalone link labels like "Live Demo", "GitHub", "Live Demo | GitHub", "Source Code"
_LINK_LABEL_TOKENS = r"[\[\(]?(?:live\s*demo|github|demo|source\s*code|live\s*link|preview|repository|repo|link|code|website|live|view\s*demo)[\]\)]?"
STANDALONE_LINK_LABELS = re.compile(
    rf"^[§•\-\*\s]*(?:{_LINK_LABEL_TOKENS}\s*(?:[|/—–•,·\-]\s*)?)+$",
    re.IGNORECASE,
)

# Tech stack delimiter pattern: "Tech Stack: React, Node, Express" or "Python — SQL — Power BI"
TECH_STACK_HEADER_REGEX = re.compile(
    r"^(?:Technologies|Tech\s*Stack|Tools)[\s:]+(.+)$",
    re.IGNORECASE,
)

TECH_STACK_DELIMITED_REGEX = re.compile(
    r"^([A-Za-z0-9+#.\s]+(?:\s*(?:—|–|\||,)\s*[A-Za-z0-9+#.\s]+)+)$",
    re.IGNORECASE,
)


def match_project_url(project_name: str, links: list[str] | None) -> str | None:
    """Match a project name to the best-fitting hyperlink extracted from document metadata."""
    if not links or not project_name:
        return None

    norm_name = re.sub(r"[^a-zA-Z0-9]", "", project_name.lower())
    significant_words = [
        w.lower() for w in re.findall(r"[A-Za-z0-9]+", project_name)
        if len(w) > 3 and w.lower() not in ("model", "dashboard", "system", "app", "project", "application")
    ]

    best_link = None
    best_score = 0

    for link in links:
        clean_link = link.split("?")[0].rstrip("/")
        slug = clean_link.split("/")[-1].lower()
        norm_slug = re.sub(r"[^a-zA-Z0-9]", "", slug)

        # Exact normalized containment gives maximum score
        if norm_slug and (norm_slug in norm_name or norm_name in norm_slug):
            score = 10 + len(norm_slug)
        else:
            # Word-overlap scoring
            score = sum(1 for w in significant_words if w in slug)

        if score > best_score:
            best_score = score
            best_link = clean_link

    return best_link if best_score > 0 else None


def extract_technologies_from_project_text(text: str) -> list[str]:
    """Identify technical skills mentioned in the project description or tech line."""
    found: list[str] = []

    # If line is comma/dash/pipe-separated
    tokens = [s.strip() for s in re.split(r"[,|—–•/]", text) if s.strip()]
    for token in tokens:
        res = resolve_skill_alias(token)
        if res:
            canon_name, _ = res
            if canon_name not in found:
                found.append(canon_name)

    # General taxonomy fallback
    for _category, skills in SKILL_TAXONOMY.items():
        for canonical_name, pattern in skills:
            if re.search(pattern, text, re.IGNORECASE):
                if canonical_name not in found:
                    found.append(canonical_name)

    return found


def unwrap_continued_lines(lines: list[str]) -> list[str]:
    """Join wrapped bullet-point lines back into complete thoughts."""
    joined: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if joined:
            prev = joined[-1]
            is_bullet = stripped.startswith(("•", "–", "-", "*")) or re.match(r"^\d+\.", stripped)
            # Conditions indicating line is a continuation of the previous bullet point
            if not is_bullet and (
                stripped[0].islower()
                or prev.rstrip().endswith((",", "-", "–", "and", "or", "to", "by", "with", "for", "in", "of"))
                or (len(stripped.split()) <= 4 and stripped.endswith(".") and prev.startswith(("•", "–", "-", "*")))
            ):
                joined[-1] = f"{prev} {stripped}"
                continue

        joined.append(stripped)
    return joined


def parse_project_entries(
    project_lines: list[str],
    links: list[str] | None = None,
) -> list[ProjectEntry]:
    """
    Parse lines from the projects section into structured ProjectEntry items.

    Removes standalone hyperlink labels like 'Live Demo' from project descriptions.
    """
    if not project_lines:
        return []

    cleaned_lines = unwrap_continued_lines(project_lines)

    # Partition lines into discrete project blocks
    blocks: list[list[str]] = []
    current_block: list[str] = []

    for line in cleaned_lines:
        is_bullet = line.startswith(("•", "–", "-", "*")) or re.match(r"^\d+\.", line)
        is_link_label = bool(STANDALONE_LINK_LABELS.match(line.strip()))
        is_tech_header = bool(TECH_STACK_HEADER_REGEX.match(line))

        if current_block and not is_bullet and not is_link_label and not is_tech_header:
            has_bullets = any(
                l.startswith(("•", "–", "-", "*")) or re.match(r"^\d+\.", l)
                for l in current_block
            )
            if has_bullets:
                blocks.append(current_block)
                current_block = []

        current_block.append(line)

    if current_block:
        blocks.append(current_block)

    entries: list[ProjectEntry] = []

    for block in blocks:
        if not block:
            continue

        project_name = None
        project_url = None
        tech_lines: list[str] = []
        desc_lines: list[str] = []

        for line in block:
            # Check for inline URL
            url_match = URL_REGEX.search(line)
            if url_match and not project_url:
                project_url = url_match.group(0).rstrip(".,;:)>]")

            # Filter out standalone hyperlink labels (e.g. "Live Demo", "GitHub", "Live Demo | GitHub")
            if STANDALONE_LINK_LABELS.match(line.strip()):
                continue

            cleaned_line = line.strip()
            if not cleaned_line:
                continue

            # First valid line is the project name
            if not project_name:
                clean_name = URL_REGEX.sub("", cleaned_line).strip(" -—–|:")
                if clean_name and not STANDALONE_LINK_LABELS.match(clean_name):
                    project_name = clean_name
                    continue

            # Check for explicit tech stack line
            tech_header_match = TECH_STACK_HEADER_REGEX.match(cleaned_line)
            if tech_header_match:
                tech_lines.append(tech_header_match.group(1))
                continue

            if TECH_STACK_DELIMITED_REGEX.match(cleaned_line) and "—" in cleaned_line:
                tech_lines.append(cleaned_line)
                continue

            # Otherwise line belongs to description
            desc_lines.append(cleaned_line)

        if not project_name:
            continue

        # Fallback to matching project URL from PDF link annotations
        if not project_url:
            project_url = match_project_url(project_name, links)

        full_block_text = " ".join(block)
        technologies = extract_technologies_from_project_text(
            " ".join(tech_lines) if tech_lines else full_block_text
        )

        description = "\n".join(desc_lines).strip() if desc_lines else None

        entries.append(
            ProjectEntry(
                project_name=project_name,
                description=description,
                technologies=technologies,
                project_url=project_url,
            )
        )

    return entries
