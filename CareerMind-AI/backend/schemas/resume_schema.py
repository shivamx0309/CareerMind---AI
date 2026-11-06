
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
