"""
Contact and personal information parser for resume text.

Extracts candidate name, email, phone number, LinkedIn, GitHub, portfolio URL,
and location using deterministic pattern matching and heuristic filtering.
"""

import re
from schemas.candidate_schema import PersonalInformation


# Common words that disqualify a line from being a candidate's personal name
NAME_BLACKLIST_WORDS = {
    "resume", "curriculum", "vitae", "cv", "summary", "profile", "contact",
    "experience", "education", "skills", "projects", "certifications",
    "engineer", "developer", "architect", "manager", "intern", "associate",
    "analyst", "student", "candidate", "page", "phone", "email", "address",
}

# Regex patterns
EMAIL_REGEX = re.compile(
    r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    re.IGNORECASE,
)

PHONE_REGEX = re.compile(
    r"(?:(?:\+|00)?\d{1,3}[\s.-]?)?(?:\(?\d{2,5}\)?[\s.-]?)?\d{3,5}[\s.-]?\d{3,5}",
)

LINKEDIN_TEXT_REGEX = re.compile(
    r"(?:https?://)?(?:www\.)?linkedin\.com/in/([a-zA-Z0-9_-]+)/?",
    re.IGNORECASE,
)

GITHUB_TEXT_REGEX = re.compile(
    r"(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_-]+)(?:/[a-zA-Z0-9_.-]+)?/?",
    re.IGNORECASE,
)

GENERIC_URL_REGEX = re.compile(
    r"https?://(?:www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+(?:/[^\s]*)?",
    re.IGNORECASE,
)

LOCATION_REGEX = re.compile(
    r"^(?:location|address)[\s:]*([A-Za-z\s,.-]+)$",
    re.IGNORECASE,
)


def extract_full_name(header_lines: list[str]) -> str | None:
    """
    Extract candidate full name from header lines.

    Heuristic:
    - Typically found in the first 3-5 lines of the resume.
    - Consists of 2 to 4 alphabetic words.
    - Excludes lines containing emails, URLs, digits, or common resume titles.
    - Returns title-cased name string or None if unidentifiable.
    """
    for line in header_lines[:5]:
        stripped = line.strip()
        if not stripped:
            continue

        # Reject lines with emails, web links, or digits
        if "@" in stripped or "http" in stripped.lower() or "www." in stripped.lower():
            continue
        if re.search(r"\d", stripped):
            continue

        # Clean noise characters (bullets, icons, non-letters except hyphens and dots)
        cleaned = re.sub(r"[^a-zA-Z\s.-]", " ", stripped)
        words = [w for w in cleaned.split() if len(w) > 1 or w.endswith(".")]

        # Candidate name should have 2 to 4 words
        if 2 <= len(words) <= 4:
            # Check for blacklisted role/heading words
            lower_words = {w.lower().rstrip(".:;,") for w in words}
            if lower_words.intersection(NAME_BLACKLIST_WORDS):
                continue

            # Check word lengths (names don't usually have single-character words except initials)
            if all(len(w.rstrip(".")) >= 2 or w.endswith(".") for w in words):
                candidate_name = " ".join(words)
                # Normalize all-caps to Title Case, preserve intentional casing otherwise
                if candidate_name.isupper() or candidate_name.islower():
                    return candidate_name.title()
                return candidate_name

    return None


def extract_email(text: str, links: list[str] | None = None) -> str | None:
    """Extract primary contact email address from text and link references."""
    # Check text first
    match = EMAIL_REGEX.search(text)
    if match:
        email = match.group(0).strip().rstrip(".,;:)>]")
        return email.lower()

    # Fallback to link annotations (e.g. mailto: links)
    if links:
        for link in links:
            if link.lower().startswith("mailto:"):
                clean_email = link[7:].split("?")[0].strip()
                if EMAIL_REGEX.match(clean_email):
                    return clean_email.lower()

    return None


def extract_phone(text: str, links: list[str] | None = None) -> str | None:
    """
    Extract contact phone number.

    Validates that the extracted number contains 10 to 15 digits
    and is not an address zipcode or year range.
    """
    # Check tel: link annotations first for clean fidelity
    if links:
        for link in links:
            if link.lower().startswith("tel:"):
                raw_tel = link[4:].strip()
                digits = re.sub(r"\D", "", raw_tel)
                if 10 <= len(digits) <= 15:
                    return f"+{digits}" if raw_tel.startswith("+") else digits

    # Scan text for phone numbers
    matches = PHONE_REGEX.findall(text)
    for candidate in matches:
        digits = re.sub(r"\D", "", candidate)
        # Check digit count
        if 10 <= len(digits) <= 15:
            # Exclude year ranges like 20202024
            if len(digits) == 8 and (digits.startswith("19") or digits.startswith("20")):
                continue
            cleaned = candidate.strip().rstrip(".,;:")
            # If candidate was preceded by + in text
            if f"+{candidate.strip()}" in text or candidate.strip().startswith("+"):
                return f"+{digits}" if not cleaned.startswith("+") else cleaned
            return cleaned

    return None


def extract_linkedin(text: str, links: list[str] | None = None) -> str | None:
    """Extract LinkedIn profile URL."""
    # Check links list
    if links:
        for link in links:
            if "linkedin.com/in/" in link.lower():
                return link.split("?")[0].rstrip("/")

    # Check text
    match = LINKEDIN_TEXT_REGEX.search(text)
    if match:
        username = match.group(1).rstrip("/")
        return f"https://www.linkedin.com/in/{username}"

    return None


def extract_github(text: str, links: list[str] | None = None) -> str | None:
    """Extract candidate personal GitHub profile URL."""
    # Check links list
    if links:
        profile_links = []
        for link in links:
            clean = link.split("?")[0].rstrip("/")
            if "github.com/" in clean.lower():
                parts = clean.split("github.com/")[-1].split("/")
                # Top-level username only (1 path segment)
                if len(parts) == 1 and parts[0]:
                    return f"https://github.com/{parts[0]}"
                profile_links.append(clean)
        if profile_links:
            # If only repo links found, candidate username is the owner
            owner = profile_links[0].split("github.com/")[-1].split("/")[0]
            if owner:
                return f"https://github.com/{owner}"

    # Check text
    match = GITHUB_TEXT_REGEX.search(text)
    if match:
        username = match.group(1).rstrip("/")
        return f"https://github.com/{username}"

    return None


def extract_portfolio(
    text: str,
    linkedin_url: str | None = None,
    github_url: str | None = None,
    links: list[str] | None = None,
) -> str | None:
    """Extract personal portfolio or website URL."""
    excluded_domains = {"linkedin.com", "github.com", "google.com", "t.co", "facebook.com", "twitter.com", "x.com"}

    # Check text for explicit Portfolio or Website label
    labeled = re.search(r"(?:portfolio|website|homepage)[\s:]+(https?://[^\s]+)", text, re.I)
    if labeled:
        return labeled.group(1).rstrip(".,;:)>]")

    # Check links list
    if links:
        for link in links:
            clean = link.split("?")[0].rstrip(".,;:/")
            if not clean.startswith(("http://", "https://")):
                continue
            domain = clean.split("//")[-1].split("/")[0].lower()
            if any(ex in domain for ex in excluded_domains):
                continue
            return clean

    # Check generic URLs in text
    for match in GENERIC_URL_REGEX.finditer(text):
        url = match.group(0).rstrip(".,;:)>]")
        domain = url.split("//")[-1].split("/")[0].lower()
        if any(ex in domain for ex in excluded_domains):
            continue
        return url

    return None


def extract_location(header_lines: list[str]) -> str | None:
    """Extract residential location (city, state, country) if present."""
    for line in header_lines:
        stripped = line.strip()
        # Look for explicit label
        match = LOCATION_REGEX.match(stripped)
        if match:
            return match.group(1).strip()

        # Check for City, State / Country patterns
        # e.g., "Agra, India", "Seattle, WA", "Bengaluru, Karnataka, India"
        if "," in stripped and len(stripped.split()) <= 5:
            # Ensure line does not contain phone, email, or URL
            if not any(ch in stripped for ch in ("@", "http", "www", "+", "/")):
                parts = [p.strip() for p in stripped.split(",") if p.strip()]
                if 2 <= len(parts) <= 3 and all(p.replace(" ", "").isalpha() for p in parts):
                    return stripped

    return None


def parse_contact_information(
    header_lines: list[str],
    full_text: str,
    links: list[str] | None = None,
) -> PersonalInformation:
    """
    Parse complete personal and contact information.

    Args:
        header_lines: Lines preceding the first major section header.
        full_text: Full document text for fallback searches.
        links: Optional hyperlink URIs extracted from document metadata.

    Returns:
        Structured PersonalInformation instance.
    """
    full_name = extract_full_name(header_lines)
    email = extract_email(full_text, links=links)
    phone = extract_phone(full_text, links=links)
    linkedin = extract_linkedin(full_text, links=links)
    github = extract_github(full_text, links=links)
    portfolio = extract_portfolio(full_text, linkedin, github, links=links)
    location = extract_location(header_lines)

    return PersonalInformation(
        full_name=full_name,
        email=email,
        phone=phone,
        linkedin=linkedin,
        github=github,
        portfolio=portfolio,
        location=location,
    )

