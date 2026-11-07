"""
Work experience and internship parser for resume text.

Correctly identifies and distinguishes:
- Designation / Job title
- Employer / Company name
- Employment type (Internship, Full-time, Associate, Contract, etc.)
- Location / Work mode (Remote, Hybrid, On-site, City, State)
- Start date and End date
- Responsibilities / description bullet points
- Technologies utilized (filtering out prose false positives like 'regression testing')
"""

import re
from schemas.candidate_schema import ExperienceEntry
from resume_engine.skills_parser import SKILL_TAXONOMY


# Date range pattern matching "June 2026 – Sep 2026", "Jul 2024 - Aug 2024", "2020 - 2023", "Jun 2026 · Present"
DATE_RANGE_REGEX = re.compile(
    r"\b((?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+)?(?:19|20)\d{2})\b\s*[-–—·to\s]+\s*\b((?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+)?(?:19|20)\d{2}|Present|Current)\b",
    re.IGNORECASE,
)

# Common delimiters between title and company: "Title — Company", "Title | Company", "Title at Company"
TITLE_COMPANY_SEPARATORS = re.compile(
    r"\s*(?:—|–|-|·|•|\||\bat\b|@)\s*",
    re.IGNORECASE,
)

# Known employment types
EMPLOYMENT_TYPES = [
    (r"\bintern(?:ship)?\b", "Internship"),
    (r"\bpart[\s-]*time\b", "Part-time"),
    (r"\bfull[\s-]*time\b", "Full-time"),
    (r"\bcontract(?:or)?\b", "Contract"),
    (r"\bfreelanc(?:e|er)\b", "Freelance"),
    (r"\bassociate\b", "Associate"),
]

# Common job designation keywords
TITLE_KEYWORDS = re.compile(
    r"\b(?:software\s+development\s+engineer|software\s+engineer|engineer|developer|intern(?:ship)?|associate|manager|lead|analyst|architect|consultant|specialist|designer|director|officer|coordinator|fellow|trainee|scientist|researcher|contributor|assistant|representative|executive|programmer)\b",
    re.IGNORECASE,
)

# Location and work mode indicators
LOCATION_REGEX = re.compile(
    r"^(?:remote|hybrid|on-site|onsite)$|^[A-Za-z\s.-]+,\s*[A-Za-z\s.-]+$",
    re.IGNORECASE,
)

# Common company suffixes
COMPANY_SUFFIXES = re.compile(
    r"\b(?:limited|ltd|inc|corp|corporation|llc|technologies|technology|labs|solutions|systems|industries|company|co)\b",
    re.IGNORECASE,
)


def extract_employment_type(text: str) -> str | None:
    """Detect employment type (e.g. Internship, Full-time) from title or text."""
    for pattern, canonical in EMPLOYMENT_TYPES:
        if re.search(pattern, text, re.IGNORECASE):
            return canonical
    return None


def extract_technologies_from_experience_text(text: str) -> list[str]:
    """
    Extract technologies mentioned in experience text.
    Protects against false positives from prose (e.g. 'regression testing' != 'Regression' ML).
    """
    found: list[str] = []

    for category, skills in SKILL_TAXONOMY.items():
        for canonical_name, pattern in skills:
            # Prevent 'Regression' match if it's 'regression testing'
            if canonical_name == "Regression" and re.search(r"\bregression\s+testing\b", text, re.I):
                continue

            if re.search(pattern, text, re.IGNORECASE):
                if canonical_name not in found:
                    found.append(canonical_name)

    return found


def classify_header_lines(lines: list[str]) -> tuple[str | None, str | None, str | None]:
    """
    Classify header lines into (job_title, company, location).

    Distinguishes company names from job designations and location/remote tags.
    """
    job_title = None
    company = None
    location = None

    remaining: list[str] = []
    for line in lines:
        cleaned = line.strip()
        if not cleaned:
            continue
        # Check for explicit location / work mode
        if LOCATION_REGEX.match(cleaned) or cleaned.lower().startswith("location:"):
            loc_val = cleaned.split(":", 1)[-1].strip() if ":" in cleaned else cleaned
            location = loc_val
        else:
            remaining.append(cleaned)

    # Check for delimited line (e.g. "Software Engineer — Acme Corp")
    delimited = False
    for r in remaining:
        parts = TITLE_COMPANY_SEPARATORS.split(r)
        if len(parts) >= 2:
            p0, p1 = parts[0].strip(), parts[1].strip()
            delimited = True
            if TITLE_KEYWORDS.search(p0):
                job_title, company = p0, p1
            else:
                company, job_title = p0, p1
            break

    if not delimited and remaining:
        for r in remaining:
            # Check if this line is a designation
            if not job_title and TITLE_KEYWORDS.search(r):
                job_title = r
            # Check if line has company suffix
            elif not company and COMPANY_SUFFIXES.search(r):
                company = r
            elif not company:
                company = r
            elif not job_title:
                job_title = r

    return job_title, company, location


def parse_title_and_company(lines: list[str]) -> tuple[str | None, str | None]:
    """
    Extract job title and company from header lines (backward compatibility).
    """
    title, company, _ = classify_header_lines(lines)
    return title, company


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


def parse_experience_entries(experience_lines: list[str]) -> list[ExperienceEntry]:
    """
    Parse lines from the experience section into structured ExperienceEntry items.

    Accurately maps:
    - Multi-line company/location/title/date headers
    - Delimited title — company headers
    - Multiple work experience and internship entries
    """
    if not experience_lines:
        return []

    # Find all date range line indices
    date_indices: list[int] = []
    for i, line in enumerate(experience_lines):
        if DATE_RANGE_REGEX.search(line):
            date_indices.append(i)

    entries: list[ExperienceEntry] = []

    if date_indices:
        prev_end = 0
        for idx, date_idx in enumerate(date_indices):
            header_lines = experience_lines[prev_end:date_idx]
            date_line = experience_lines[date_idx]

            # Determine where description ends and next entry begins
            if idx + 1 < len(date_indices):
                next_date_idx = date_indices[idx + 1]
                # Walk backward from next_date_idx over non-bullet lines (next header lines)
                k = next_date_idx - 1
                while k > date_idx and not experience_lines[k].strip().startswith(("•", "–", "-", "*")):
                    k -= 1
                next_entry_start = k + 1
                desc_raw = experience_lines[date_idx + 1:next_entry_start]
                prev_end = next_entry_start
            else:
                desc_raw = experience_lines[date_idx + 1:]

            # Parse start and end date
            date_match = DATE_RANGE_REGEX.search(date_line)
            start_date = date_match.group(1).strip() if date_match else None
            end_date = date_match.group(2).strip() if date_match else None

            # Parse title, company, and location
            job_title, company, location = classify_header_lines(header_lines)

            # Clean and unwrap description
            clean_desc_lines = unwrap_continued_lines(desc_raw)
            # Filter out any trailing location that leaked into description
            final_desc_lines = []
            for d in clean_desc_lines:
                if LOCATION_REGEX.match(d) and not location:
                    location = d
                elif not LOCATION_REGEX.match(d):
                    final_desc_lines.append(d)

            description = "\n".join(final_desc_lines).strip() if final_desc_lines else None
            full_block_text = " ".join(header_lines + [date_line] + final_desc_lines)
            technologies = extract_technologies_from_experience_text(full_block_text)
            employment_type = extract_employment_type(job_title or "") or extract_employment_type(full_block_text)

            if job_title or company:
                entries.append(
                    ExperienceEntry(
                        job_title=job_title,
                        company=company,
                        employment_type=employment_type,
                        location=location,
                        start_date=start_date,
                        end_date=end_date,
                        description=description,
                        technologies=technologies,
                    )
                )
    else:
        # Fallback if no standard date ranges found (e.g. single entry with raw lines)
        cleaned_lines = unwrap_continued_lines(experience_lines)
        job_title, company, location = classify_header_lines(cleaned_lines[:3])
        desc = "\n".join(cleaned_lines[3:]).strip() if len(cleaned_lines) > 3 else None
        if job_title or company:
            entries.append(
                ExperienceEntry(
                    job_title=job_title,
                    company=company,
                    employment_type=extract_employment_type(job_title or ""),
                    location=location,
                    start_date=None,
                    end_date=None,
                    description=desc,
                    technologies=extract_technologies_from_experience_text(" ".join(cleaned_lines)),
                )
            )

    return entries
