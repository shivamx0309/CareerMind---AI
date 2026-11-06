
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
    MAX_FILE_SIZE,
)

from schemas.resume_schema import ResumeUploadResponse


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
