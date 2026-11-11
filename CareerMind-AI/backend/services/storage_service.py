"""
Storage service abstraction for local PDF resume file operations.
Encapsulates secure path derivation, traversal protection, file I/O, and safe cleanup.
"""

import logging
import os
from pathlib import Path
import re
from typing import List, Optional, Set

logger = logging.getLogger(__name__)

# Backend and project roots
BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
DEFAULT_UPLOAD_DIR = (PROJECT_ROOT / "data" / "uploads").resolve()

# Support environment-driven upload directory (e.g. /var/data/uploads on Render persistent disk)
_env_upload_dir = os.getenv("CAREERMIND_UPLOAD_DIR")
if _env_upload_dir and _env_upload_dir.strip():
    UPLOAD_DIR = Path(_env_upload_dir.strip()).resolve()
else:
    UPLOAD_DIR = DEFAULT_UPLOAD_DIR

# Automatically ensure upload directory exists
try:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
except OSError as exc:
    logger.warning("Could not create uploads directory '%s': %s", UPLOAD_DIR, exc)

HEX_32_REGEX = re.compile(r"^[0-9a-f]{32}$", re.IGNORECASE)


def validate_file_id(file_id: str) -> str:
    """Validate that file_id is strictly a 32-character hexadecimal string."""
    if not file_id or not isinstance(file_id, str):
        raise ValueError("Invalid file ID: must be a non-empty string.")
    cleaned = file_id.strip().lower()
    if not HEX_32_REGEX.match(cleaned):
        raise ValueError(f"Invalid file ID format: '{file_id}'. Must be a 32-char hex string.")
    return cleaned


def get_file_path(file_id: str, base_dir: Optional[Path] = None) -> Path:
    """
    Derive the secure physical PDF path server-side from the validated file_id.
    Guarantees path containment to prevent directory traversal attacks.
    """
    validated_id = validate_file_id(file_id)
    root = (base_dir or UPLOAD_DIR).resolve()
    target_path = (root / f"{validated_id}.pdf").resolve()

    try:
        target_path.relative_to(root)
    except ValueError as exc:
        raise ValueError("Invalid file path: path traversal detected.") from exc

    return target_path


def file_exists(file_id: str, base_dir: Optional[Path] = None) -> bool:
    """Check if a stored resume file exists on disk."""
    try:
        path = get_file_path(file_id, base_dir=base_dir)
        return path.exists() and path.is_file()
    except ValueError:
        return False


def get_file_bytes(file_id: str, base_dir: Optional[Path] = None) -> bytes:
    """Retrieve raw bytes of a stored file. Raises FileNotFoundError if not found."""
    path = get_file_path(file_id, base_dir=base_dir)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Resume file '{file_id}.pdf' not found.")
    return path.read_bytes()


# Alias for get_file_bytes
get_file = get_file_bytes


def save_file(file_id: str, file_bytes: bytes, base_dir: Optional[Path] = None) -> Path:
    """Save raw file bytes to the upload directory under {file_id}.pdf."""
    target_dir = base_dir or UPLOAD_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    path = get_file_path(file_id, base_dir=target_dir)
    path.write_bytes(file_bytes)
    return path


def delete_file(file_id: str, base_dir: Optional[Path] = None) -> bool:
    """
    Safely delete a stored PDF file from disk.
    Guarantees containment: will never delete outside the validated uploads directory.
    Catches and logs OSError/PermissionError so OS-level locks don't crash callers.
    Returns True if deleted, False if file did not exist or could not be removed.
    """
    try:
        path = get_file_path(file_id, base_dir=base_dir)
        if path.exists() and path.is_file():
            path.unlink()
            return True
        return False
    except ValueError:
        return False
    except (OSError, PermissionError) as exc:
        logger.warning(
            "Safe cleanup warning: could not unlink resume file '%s' on disk (%s: %s). "
            "File may be locked by another process or read-only.",
            file_id,
            type(exc).__name__,
            exc,
        )
        return False


def find_orphaned_files(known_file_ids: Set[str], base_dir: Optional[Path] = None) -> List[Path]:
    """
    Identify physical files in the upload directory that do not correspond to any registered database record.
    Useful for future vacuum/maintenance tasks.
    """
    target_dir = (base_dir or UPLOAD_DIR).resolve()
    if not target_dir.exists():
        return []

    orphans = []
    for pdf_file in target_dir.glob("*.pdf"):
        stem = pdf_file.stem.lower()
        if stem not in known_file_ids:
            orphans.append(pdf_file)
    return orphans


def cleanup_orphaned_files(known_file_ids: Set[str], base_dir: Optional[Path] = None) -> int:
    """
    Safely delete stale/orphaned files that have no matching database record.
    Returns the count of successfully deleted files.
    """
    orphans = find_orphaned_files(known_file_ids, base_dir=base_dir)
    deleted_count = 0
    for file_path in orphans:
        try:
            file_path.unlink()
            deleted_count += 1
            logger.info("Maintenance cleanup: removed orphaned file '%s'", file_path.name)
        except (OSError, PermissionError) as exc:
            logger.warning("Maintenance cleanup: could not remove orphaned file '%s': %s", file_path.name, exc)
    return deleted_count
