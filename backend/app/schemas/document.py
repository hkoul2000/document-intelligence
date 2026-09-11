from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class FileValidationResponse(BaseModel):
    valid: bool
    file_type: str | None = None
    page_count: int | None = None
    error: str | None = None


class DocumentTypeValidationResponse(BaseModel):
    valid: bool
    document_type: str | None = None
    error: str | None = None


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_name: str
    document_type: str
    status: str
    file_validation: dict[str, Any] | None = None
    extracted_data: dict[str, Any] | None = None
    validation_checks: list[dict[str, Any]] | None = None
    created_at: datetime


class DocumentListItem(BaseModel):
    id: int
    document_name: str
    document_type: str
    status: str
    created_at: datetime


class DocumentListResponse(BaseModel):
    count: int
    documents: list[DocumentListItem]