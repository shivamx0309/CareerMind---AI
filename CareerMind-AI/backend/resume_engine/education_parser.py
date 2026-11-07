"""
Education information parser for resume text.

Extracts educational credentials including degree, institution,
specialization, graduation timeline, and grade/CGPA.
Supports single and multiple education entries.
"""

import re
from schemas.candidate_schema import EducationEntry


# Common degree patterns
DEGREE_KEYWORDS = [
    (r"\bBachelor\s+of\s+Engineering\b", "Bachelor of Engineering"),
    (r"\bBachelor\s+of\s+Technology\b", "Bachelor of Technology"),
    (r"\bBachelor\s+of\s+Science\b", "Bachelor of Science"),
    (r"\bBachelor\s+of\s+Arts\b", "Bachelor of Arts"),
    (r"\bBachelor\s+of\s+Commerce\b", "Bachelor of Commerce"),
    (r"\bBachelor\s+of\s+Business\s+Administration\b", "Bachelor of Business Administration"),
    (r"\bMaster\s+of\s+Technology\b", "Master of Technology"),
    (r"\bMaster\s+of\s+Science\b", "Master of Science"),
    (r"\bMaster\s+of\s+Engineering\b", "Master of Engineering"),
    (r"\bMaster\s+of\s+Business\s+Administration\b", "Master of Business Administration"),
    (r"\bMaster\s+of\s+Arts\b", "Master of Arts"),
    (r"\bDoctor\s+of\s+Philosophy\b", "Doctor of Philosophy"),
    (r"\bB\.?Tech\b", "B.Tech"),
    (r"\bM\.?Tech\b", "M.Tech"),
    (r"\bB\.?E\.?\b", "B.E."),
    (r"\bM\.?E\.?\b", "M.E."),
    (r"\bB\.?S\.?C?\.?\b", "B.S."),
    (r"\bM\.?S\.?C?\.?\b", "M.S."),
    (r"\bB\.?C\.?A\.?\b", "BCA"),
    (r"\bM\.?C\.?A\.?\b", "MCA"),
    (r"\bM\.?B\.?A\.?\b", "MBA"),
    (r"\bPh\.?D\.?\b", "Ph.D."),
    (r"\bDiploma\b", "Diploma"),
    (r"\bHigh\s+School\b", "High School"),
    (r"\bSenior\s+Secondary\b", "Senior Secondary"),
    (r"\bIntermediate\b", "Intermediate"),
]

# Year patterns
YEAR_RANGE_REGEX = re.compile(
    r"\b((?:19|20)\d{2})\b\s*[-–—·to\s]+\s*\b((?:19|20)\d{2}|Present|Current|Expected)\b",
    re.IGNORECASE,
)
SINGLE_YEAR_REGEX = re.compile(
    r"\b((?:19|20)\d{2})\b",
)

# Grade / CGPA patterns
GRADE_REGEX = re.compile(
    r"(?:CGPA|GPA|Grade|Score|Percentage)[\s:]*([0-9]+(?:\.[0-9]+)?(?:\s*/\s*[0-9]+(?:\.[0-9]+)?)?%?)",
    re.IGNORECASE,
)
STANDALONE_CGPA_REGEX = re.compile(
    r"\b([0-9]\.[0-9]{1,2}\s*/\s*(?:10|4(?:\.0)?))\b",
)
PERCENTAGE_REGEX = re.compile(
    r"\b([1-9][0-9](?:\.[0-9]+)?%)\b",
)

# Institution keywords
INSTITUTION_INDICATORS = [
    "university", "institute", "college", "school", "academy", "polytechnic", "vidyalaya",
]


def extract_degree_and_specialization(line: str) -> tuple[str | None, str | None]:
    """Extract degree name and specialization from a line of text."""
    degree = None
    specialization = None

    # Check for known degree patterns
    for pattern, canonical in DEGREE_KEYWORDS:
        if re.search(pattern, line, re.IGNORECASE):
            degree = canonical
            break

    if degree:
        # Check for specialization in parentheses: "Bachelor of Engineering (Computer Science Engineering)"
        paren_match = re.search(r"\(([^)]+)\)", line)
        if paren_match:
            cand_spec = paren_match.group(1).strip()
            # Make sure it's not a year or location
            if not re.search(r"\d{4}", cand_spec):
                specialization = cand_spec
        else:
            # Check for "in <Specialization>": "B.Tech in Computer Science"
            in_match = re.search(r"\bin\s+([A-Za-z\s&,-]+?)(?:,|$|\s*[-–|])", line, re.IGNORECASE)
            if in_match:
                specialization = in_match.group(1).strip()

    return degree, specialization


def extract_institution(line: str) -> str | None:
    """Identify whether a line contains an educational institution name."""
    lower_line = line.lower()
    if any(indicator in lower_line for indicator in INSTITUTION_INDICATORS):
        # Exclude lines that are purely core concepts or achievements
        if not lower_line.startswith(("core concepts", "projects", "achievements", "courses")):
            return line.strip()
    return None


def extract_years(text: str) -> tuple[str | None, str | None]:
    """Extract start and end graduation years."""
    range_match = YEAR_RANGE_REGEX.search(text)
    if range_match:
        start = range_match.group(1)
        end = range_match.group(2)
        return start, end

    single_matches = SINGLE_YEAR_REGEX.findall(text)
    if len(single_matches) >= 2:
        return single_matches[0], single_matches[1]
    if len(single_matches) == 1:
        return None, single_matches[0]

    return None, None


def extract_grade(text: str) -> str | None:
    """Extract CGPA, GPA, or percentage."""
    match = GRADE_REGEX.search(text)
    if match:
        return match.group(1).strip()

    match = STANDALONE_CGPA_REGEX.search(text)
    if match:
        return match.group(1).strip()

    match = PERCENTAGE_REGEX.search(text)
    if match:
        return match.group(1).strip()

    return None


def parse_education_entries(education_lines: list[str]) -> list[EducationEntry]:
    """
    Parse lines from the education section into structured EducationEntry items.
    Supports single or multiple educational qualifications.
    """
    if not education_lines:
        return []

    # Partition lines into blocks per qualification
    blocks: list[list[str]] = []
    current_block: list[str] = []

    for line in education_lines:
        stripped = line.strip()
        if not stripped:
            if current_block:
                blocks.append(current_block)
                current_block = []
            continue

        # Check if line indicates the start of a new degree entry
        degree_found, _ = extract_degree_and_specialization(stripped)
        if degree_found and current_block:
            # If current block already contains a degree, finalize it and start new block
            block_has_degree = any(extract_degree_and_specialization(l)[0] for l in current_block)
            if block_has_degree:
                blocks.append(current_block)
                current_block = []

        current_block.append(stripped)

    if current_block:
        blocks.append(current_block)

    entries: list[EducationEntry] = []

    for block in blocks:
        block_text = " ".join(block)
        degree = None
        specialization = None
        institution = None
        start_year, end_year = extract_years(block_text)
        grade = extract_grade(block_text)

        for line in block:
            # Check for degree and specialization
            if not degree:
                deg, spec = extract_degree_and_specialization(line)
                if deg:
                    degree = deg
                    if spec:
                        specialization = spec

            # Check for institution
            if not institution:
                inst = extract_institution(line)
                if inst:
                    institution = inst

        # Only add entry if at least a degree or institution was detected
        if degree or institution:
            entries.append(
                EducationEntry(
                    degree=degree,
                    institution=institution,
                    specialization=specialization,
                    start_year=start_year,
                    end_year=end_year,
                    grade_or_cgpa=grade,
                )
            )

    return entries
