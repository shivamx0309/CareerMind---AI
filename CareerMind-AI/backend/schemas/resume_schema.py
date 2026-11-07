
from pydantic import BaseModel, Field


class ResumeUploadResponse(BaseModel):

    success: bool = True

    message: str

    file_id: str

    original_filename: str

    file_size_bytes: int = Field(ge=1)

    content_type: str

    page_count: int = Field(ge=1)

    extraction_status: str = "pending"


class ResumePageText(BaseModel):

    page_number: int = Field(ge=1, description="1-indexed page number")

    text: str = Field(description="Extracted and normalized text of the page")

    character_count: int = Field(
        ge=0, description="Total characters on this page"
    )


class ResumeExtractionResponse(BaseModel):

    success: bool = True

    file_id: str = Field(
        description="Unique 32-character hexadecimal file identifier"
    )

    page_count: int = Field(
        ge=1, description="Total number of pages in the PDF document"
    )

    character_count: int = Field(
        ge=0, description="Total character count across all extracted pages"
    )

    extraction_status: str = Field(
        description="Status of the extraction (e.g. 'completed')"
    )

    full_text: str = Field(
        description="Consolidated full text extracted from the document"
    )

    pages: list[ResumePageText] = Field(
        description="Page-by-page structured text breakdown"
    )

    original_filename: str | None = Field(
        default=None,
        description="Original uploaded filename if available in metadata",
    )

