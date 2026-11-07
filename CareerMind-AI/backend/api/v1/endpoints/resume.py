
from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    status,
)

from resume_engine.file_validator import (
    validate_pdf_file,
    validate_file_id,
    MAX_FILE_SIZE,
)
from resume_engine.text_extractor import extract_text_from_pdf
from resume_engine.information_extractor import extract_candidate_profile
from schemas.resume_schema import (
    ResumeUploadResponse,
    ResumeExtractionResponse,
)
from schemas.candidate_schema import ResumeParseResponse


router = APIRouter()

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[4]

# Resume upload directory
UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"


@router.post(
    "/resumes/upload",
    response_model=ResumeUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_resume(
    file: UploadFile = File(...)
):
    """Upload and validate a candidate resume."""

    chunks = []
    total_size = 0

    try:
        # Read file in 1 MB chunks
        while True:
            chunk = await file.read(1024 * 1024)

            if not chunk:
                break

            total_size += len(chunk)

            # Maximum size check
            if total_size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail="File exceeds the 5 MB limit.",
                )

            chunks.append(chunk)

        file_bytes = b"".join(chunks)

        # Validate PDF
        try:
            page_count = validate_pdf_file(
                filename=file.filename or "",
                content_type=file.content_type,
                file_bytes=file_bytes,
            )

        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        # Generate unique ID
        file_id = uuid4().hex

        # Create upload directory
        UPLOAD_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        # Save PDF using generated filename
        stored_path = UPLOAD_DIR / f"{file_id}.pdf"

        stored_path.write_bytes(file_bytes)

        # Return structured response
        return ResumeUploadResponse(
            success=True,
            message="Resume uploaded successfully.",
            file_id=file_id,
            original_filename=file.filename or "resume.pdf",
            file_size_bytes=total_size,
            content_type="application/pdf",
            page_count=page_count,
            extraction_status="pending",
        )

    finally:
        await file.close()


@router.post(
    "/resumes/{file_id}/extract",
    response_model=ResumeExtractionResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract text from an uploaded resume PDF",
)
async def extract_resume(file_id: str):
    """
    Extract text and page-by-page content from an already uploaded resume PDF.

    - Validates that `file_id` is a 32-character hexadecimal UUID.
    - Locates the stored PDF in the uploads directory without requiring re-upload.
    - Enforces path containment to prevent directory traversal.
    - Extracts structured text using PyMuPDF.
    - Returns HTTP 400 for invalid file IDs.
    - Returns HTTP 404 if the resume file does not exist.
    - Returns HTTP 422 if the document is unreadable, corrupted, or contains no readable text.
    """
    # 1. Validate file ID format
    try:
        validated_file_id = validate_file_id(file_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    # 2. Resolve target file path and prevent directory traversal
    upload_dir_resolved = UPLOAD_DIR.resolve()
    stored_path = (UPLOAD_DIR / f"{validated_file_id}.pdf").resolve()

    try:
        stored_path.relative_to(upload_dir_resolved)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file path.",
        ) from exc

    # 3. Verify file existence
    if not stored_path.exists() or not stored_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume file not found.",
        )

    # 4. Extract text via resume_engine
    try:
        extraction_data = extract_text_from_pdf(str(stored_path))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unable to extract text from the PDF document.",
        ) from exc

    # 5. Check if readable text was found
    if (
        extraction_data.get("extraction_status") == "no_text_found"
        or not extraction_data.get("full_text", "").strip()
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No readable text found in the resume PDF.",
        )

    # 6. Return structured response
    return ResumeExtractionResponse(
        success=True,
        file_id=validated_file_id,
        page_count=extraction_data["page_count"],
        character_count=extraction_data["character_count"],
        extraction_status=extraction_data["extraction_status"],
        full_text=extraction_data["full_text"],
        pages=extraction_data["pages"],
        original_filename=None,
    )


@router.post(
    "/resumes/{file_id}/parse",
    response_model=ResumeParseResponse,
    status_code=status.HTTP_200_OK,
    summary="Parse candidate profile from an uploaded resume PDF",
)
async def parse_resume(file_id: str):
    """
    Parse candidate profile (personal info, summary, skills, education,
    experience, projects, and certifications) from an uploaded resume PDF.

    - Validates that `file_id` is a 32-character hexadecimal UUID.
    - Locates the stored PDF in the uploads directory without requiring re-upload.
    - Enforces path containment to prevent directory traversal.
    - Extracts structured text and hyperlink annotations using PyMuPDF.
    - Parses and normalizes candidate information into structured JSON.
    - Returns HTTP 400 for invalid file IDs or path traversal attempts.
    - Returns HTTP 404 if the resume file does not exist.
    - Returns HTTP 422 if the document is unreadable, corrupted, or contains no readable text.
    """
    # 1. Validate file ID format
    try:
        validated_file_id = validate_file_id(file_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    # 2. Resolve target file path and prevent directory traversal
    upload_dir_resolved = UPLOAD_DIR.resolve()
    stored_path = (UPLOAD_DIR / f"{validated_file_id}.pdf").resolve()

    try:
        stored_path.relative_to(upload_dir_resolved)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file path.",
        ) from exc

    # 3. Verify file existence
    if not stored_path.exists() or not stored_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume file not found.",
        )

    # 4. Extract text via resume_engine
    try:
        extraction_data = extract_text_from_pdf(str(stored_path))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unable to extract text from the PDF document.",
        ) from exc

    # 5. Check if readable text was found
    if (
        extraction_data.get("extraction_status") == "no_text_found"
        or not extraction_data.get("full_text", "").strip()
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No readable text found in the resume PDF.",
        )

    # 6. Parse structured candidate information
    candidate_profile = extract_candidate_profile(
        raw_text=extraction_data["full_text"],
        links=extraction_data.get("links"),
    )

    # 7. Return structured response
    return ResumeParseResponse(
        success=True,
        file_id=validated_file_id,
        candidate=candidate_profile,
    )

