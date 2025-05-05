from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
from .config import settings

class DocumentBase(BaseModel):
    """Base schema for document-related operations."""
    bsc_number: str = Field(..., min_length=1, description="BSC number associated with the document")
    category: str = Field(..., description="Document category")

    @validator('category')
    def validate_category(cls, v):
        if v not in settings.ALLOWED_CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(settings.ALLOWED_CATEGORIES)}")
        return v

class DocumentResponse(BaseModel):
    uuid: str
    bsc_number: str
    category: str
    filesize: str
    message: str

    class Config:
        from_attributes = True

class DocumentList(BaseModel):
    uuid: str
    bsc_number: str
    category: str
    page_number: int
    filesize: str
    upload_datetime: datetime

    class Config:
        from_attributes = True 