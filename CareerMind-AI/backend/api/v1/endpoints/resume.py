"""
Resume intelligence and library API endpoints.
Provides resume upload, extraction, parsing, persistent SQLite storage,
and full resume library lifecycle management.
"""

from pathlib import Path
from typing import List, Optional
from uuid import uuid4

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException,
    Depends,
    status,
)
from sqlalchemy.orm import Session

from database.session import get_db
from resume_engine.file_validator import (
    validate_pdf_file,
    MAX_FILE_SIZE,
)
from resume_engine.text_extractor import extract_text_from_pdf
from resume_engine.information_extractor import extract_candidate_profile
from schemas.resume_schema import (
    ResumeUploadResponse,
    ResumeExtractionResponse,
)
from schemas.candidate_schema import ResumeParseResponse
from schemas.resume_library_schema import (
    ResumeRecordResponse,
    ResumeRecordRename,
    ResumeDetailResponse,
)
from services import storage_service, career_profile_service, resume_library_service

router = APIRouter()

# Re-export storage_service.UPLOAD_DIR for backwards-compatibility (e.g. jobs matching endpoint and tests)
UPLOAD_DIR = storage_service.UPLOAD_DIR


# =============================================================================
# Core Resume Upload, Extraction, and Parsing Endpoints
# =============================================================================


@router.post(
    "/resumes/upload",
    response_model=ResumeUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a candidate resume PDF",
)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload and validate a candidate resume PDF.
    Persists physical file to uploads directory and registers a ResumeRecord in SQLite.
    Automatically assigns default status to the first uploaded resume.
    """
    chunks = []
    total_size = 0

    try:
        # Read file in 1 MB chunks
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break

            total_size += len(chunk)

            # Maximum size check (5 MB)
            if total_size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="File exceeds the 5 MB limit.",
                )

            chunks.append(chunk)

        file_bytes = b"".join(chunks)

        # Validate PDF structure, page count, and encryption
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

        # Generate unique 32-hex ID
        file_id = uuid4().hex

        # Save PDF using storage service abstraction
        storage_service.save_file(file_id, file_bytes, base_dir=UPLOAD_DIR)

        # Retrieve or create local career profile as owner
        career_profile = career_profile_service.get_or_create_local_career_profile(db)

        # Register resume record in SQLite database
        resume_library_service.register_uploaded_resume(
            db=db,
            career_profile_id=career_profile.id,
            file_id=file_id,
            original_filename=file.filename or "resume.pdf",
            file_size=total_size,
            base_dir=UPLOAD_DIR,
        )

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
async def extract_resume(
    file_id: str,
    db: Session = Depends(get_db),
):
    """
    Extract text and page-by-page content from an already uploaded resume PDF.
    Enforces path containment and validates file existence.
    """
    try:
        validated_file_id = storage_service.validate_file_id(file_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    try:
        file_path = storage_service.get_file_path(validated_file_id, base_dir=UPLOAD_DIR)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume file not found.",
        )

    try:
        extraction_data = extract_text_from_pdf(str(file_path))
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

    if (
        extraction_data.get("extraction_status") == "no_text_found"
        or not extraction_data.get("full_text", "").strip()
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No readable text found in the resume PDF.",
        )

    # If DB record exists, update extraction status
    profile = career_profile_service.get_local_career_profile(db)
    if profile:
        rec = resume_library_service.get_resume_record(db, profile.id, validated_file_id)
        if rec:
            rec.extraction_status = "completed"
            db.commit()

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
async def parse_resume(
    file_id: str,
    db: Session = Depends(get_db),
):
    """
    Parse candidate profile (personal info, summary, skills, education,
    experience, projects, certifications, and achievements) from an uploaded resume PDF.
    Persists structured relational entities in SQLite database idempotently.
    """
    try:
        validated_file_id = storage_service.validate_file_id(file_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    try:
        file_path = storage_service.get_file_path(validated_file_id, base_dir=UPLOAD_DIR)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume file not found.",
        )

    try:
        extraction_data = extract_text_from_pdf(str(file_path))
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

    if (
        extraction_data.get("extraction_status") == "no_text_found"
        or not extraction_data.get("full_text", "").strip()
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No readable text found in the resume PDF.",
        )

    candidate_profile = extract_candidate_profile(
        raw_text=extraction_data["full_text"],
        links=extraction_data.get("links"),
    )

    # Persist parsed CandidateProfile into SQLite if a ResumeRecord exists
    profile = career_profile_service.get_local_career_profile(db)
    if profile:
        record = resume_library_service.get_resume_record(db, profile.id, validated_file_id)
        if record:
            resume_library_service.persist_parsed_candidate_profile(
                db=db,
                resume_record_id=record.id,
                candidate=candidate_profile,
            )

    return ResumeParseResponse(
        success=True,
        file_id=validated_file_id,
        candidate=candidate_profile,
    )


# =============================================================================
# Resume Library Management Endpoints (Phase 1D)
# =============================================================================


@router.get(
    "/resumes/library",
    response_model=List[ResumeRecordResponse],
    status_code=status.HTTP_200_OK,
    summary="List all resumes in the career profile library",
)
async def list_resume_library(
    db: Session = Depends(get_db),
):
    """Retrieve all resume records for the local career profile ordered by default then creation date."""
    profile = career_profile_service.get_or_create_local_career_profile(db)
    return resume_library_service.get_resume_records(db, profile.id)


@router.post(
    "/resumes/library",
    response_model=ResumeRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload, parse, and persist a resume into the library in a single operation",
)
async def create_resume_library_entry(
    file: UploadFile = File(...),
    display_name: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """
    End-to-end pipeline: uploads, saves, extracts, parses, and persists a resume record.
    """
    chunks = []
    total_size = 0

    try:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            total_size += len(chunk)
            if total_size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="File exceeds the 5 MB limit.",
                )
            chunks.append(chunk)

        file_bytes = b"".join(chunks)

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

        file_id = uuid4().hex
        saved_path = storage_service.save_file(file_id, file_bytes, base_dir=UPLOAD_DIR)

        profile = career_profile_service.get_or_create_local_career_profile(db)
        record = resume_library_service.register_uploaded_resume(
            db=db,
            career_profile_id=profile.id,
            file_id=file_id,
            original_filename=file.filename or "resume.pdf",
            file_size=total_size,
            display_name=display_name,
            base_dir=UPLOAD_DIR,
        )

        # Extract & Parse
        try:
            extraction_data = extract_text_from_pdf(str(saved_path))
            if (
                extraction_data.get("extraction_status") == "no_text_found"
                or not extraction_data.get("full_text", "").strip()
            ):
                record.extraction_status = "failed"
                record.parsing_status = "failed"
                db.commit()
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="No readable text found in the resume PDF.",
                )

            record.extraction_status = "completed"
            candidate_profile = extract_candidate_profile(
                raw_text=extraction_data["full_text"],
                links=extraction_data.get("links"),
            )

            resume_library_service.persist_parsed_candidate_profile(
                db=db,
                resume_record_id=record.id,
                candidate=candidate_profile,
            )
            db.refresh(record)
            return record

        except HTTPException:
            raise
        except Exception as exc:
            record.parsing_status = "failed"
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to parse resume: {exc}",
            ) from exc

    finally:
        await file.close()


@router.get(
    "/resumes/library/{resume_id}",
    response_model=ResumeDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get detailed resume metadata and reconstructed candidate profile",
)
async def get_resume_library_detail(
    resume_id: str,
    db: Session = Depends(get_db),
):
    """
    Retrieve resume metadata along with the 100% faithful reconstituted CandidateProfile.
    Looks up by either database UUID or 32-hex file_id.
    """
    profile = career_profile_service.get_or_create_local_career_profile(db)
    record = resume_library_service.get_resume_record(db, profile.id, resume_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume record not found.",
        )

    candidate = resume_library_service.reconstitute_candidate_profile(db, record.id)
    return ResumeDetailResponse(
        id=record.id,
        career_profile_id=record.career_profile_id,
        file_id=record.file_id,
        display_name=record.display_name,
        original_filename=record.original_filename,
        file_path=record.file_path,
        file_size=record.file_size,
        is_default=record.is_default,
        upload_status=record.upload_status,
        extraction_status=record.extraction_status,
        parsing_status=record.parsing_status,
        created_at=record.created_at,
        updated_at=record.updated_at,
        last_parsed_at=record.last_parsed_at,
        candidate=candidate,
    )


@router.patch(
    "/resumes/library/{resume_id}",
    response_model=ResumeRecordResponse,
    status_code=status.HTTP_200_OK,
    summary="Rename resume display name",
)
async def rename_resume_library_entry(
    resume_id: str,
    payload: ResumeRecordRename,
    db: Session = Depends(get_db),
):
    """Update user-facing display name of a resume in the library."""
    profile = career_profile_service.get_or_create_local_career_profile(db)
    updated = resume_library_service.rename_resume_record(
        db=db,
        resume_record_id=resume_id,
        new_display_name=payload.display_name,
        career_profile_id=profile.id,
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume record not found.",
        )
    return updated


@router.put(
    "/resumes/library/{resume_id}/default",
    response_model=ResumeRecordResponse,
    status_code=status.HTTP_200_OK,
    summary="Designate a resume as the default",
)
async def set_default_resume_library_entry(
    resume_id: str,
    db: Session = Depends(get_db),
):
    """Atomically set a resume record as the default for the active career profile."""
    profile = career_profile_service.get_or_create_local_career_profile(db)
    try:
        updated = resume_library_service.set_default_resume(
            db=db,
            career_profile_id=profile.id,
            resume_record_id=resume_id,
        )
        return updated
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.delete(
    "/resumes/library/{resume_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a resume from library and storage",
)
async def delete_resume_library_entry(
    resume_id: str,
    db: Session = Depends(get_db),
):
    """
    Delete a resume from database and remove its PDF from disk.
    If default, promotes another remaining resume.
    """
    profile = career_profile_service.get_or_create_local_career_profile(db)
    deleted = resume_library_service.delete_resume_record(
        db=db,
        career_profile_id=profile.id,
        resume_record_id=resume_id,
        base_dir=UPLOAD_DIR,
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume record not found.",
        )
    return {"success": True, "message": "Resume deleted successfully."}


@router.post(
    "/resumes/library/{resume_id}/replace",
    response_model=ResumeRecordResponse,
    status_code=status.HTTP_200_OK,
    summary="Atomically replace an existing resume with a newly uploaded PDF",
)
async def replace_resume_library_entry(
    resume_id: str,
    file: UploadFile = File(...),
    display_name: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """
    Atomically replace a resume:
    1. Validates and parses the new PDF file first.
    2. If parsing fails, preserves original resume and disk file.
    3. If parsing succeeds, swaps DB records and deletes the old PDF file.
    """
    profile = career_profile_service.get_or_create_local_career_profile(db)
    target = resume_library_service.get_resume_record(db, profile.id, resume_id)
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume record not found.",
        )

    chunks = []
    total_size = 0

    try:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            total_size += len(chunk)
            if total_size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="File exceeds the 5 MB limit.",
                )
            chunks.append(chunk)

        file_bytes = b"".join(chunks)

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

        # Save new file to temporary file_id
        new_file_id = uuid4().hex
        new_file_path = storage_service.save_file(new_file_id, file_bytes, base_dir=UPLOAD_DIR)

        # Extract & Parse new PDF
        try:
            extraction_data = extract_text_from_pdf(str(new_file_path))
            if (
                extraction_data.get("extraction_status") == "no_text_found"
                or not extraction_data.get("full_text", "").strip()
            ):
                storage_service.delete_file(new_file_id, base_dir=UPLOAD_DIR)
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="No readable text found in the replacement resume PDF.",
                )

            candidate_profile = extract_candidate_profile(
                raw_text=extraction_data["full_text"],
                links=extraction_data.get("links"),
            )
        except HTTPException:
            storage_service.delete_file(new_file_id, base_dir=UPLOAD_DIR)
            raise
        except Exception as exc:
            storage_service.delete_file(new_file_id, base_dir=UPLOAD_DIR)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to parse replacement resume: {exc}",
            ) from exc

        # Atomic replacement in DB
        try:
            updated_record = resume_library_service.replace_resume_record(
                db=db,
                career_profile_id=profile.id,
                resume_record_id=target.id,
                new_file_id=new_file_id,
                new_original_filename=file.filename or "resume.pdf",
                new_file_size=total_size,
                new_candidate=candidate_profile,
                new_display_name=display_name,
                base_dir=UPLOAD_DIR,
            )
            return updated_record
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Replacement failed: {exc}",
            ) from exc

    finally:
        await file.close()
