"""
Document schemas for API validation.
"""
from datetime import datetime, date
from typing import Optional, List, Any
from pydantic import BaseModel

from app.models.document import DocumentStatus
from app.schemas.document_type import DocumentTypeResponse
from app.schemas.product import ProductResponse


class DocumentBase(BaseModel):
    """Base document schema."""
    title: str
    description: Optional[str] = None
    document_type_id: int
    department: str
    language: str = "DE"


class DocumentCreate(DocumentBase):
    """Schema for creating a new document."""
    product_ids: Optional[List[int]] = None


class DocumentUpdate(BaseModel):
    """Schema for updating a document."""
    title: Optional[str] = None
    description: Optional[str] = None
    department: Optional[str] = None
    language: Optional[str] = None
    effective_date: Optional[date] = None
    next_review_date: Optional[date] = None


class DocumentVersionSummary(BaseModel):
    """Summary of a document version for list views."""
    id: int
    version_major: int
    version_minor: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    """Schema for document response."""
    id: int
    document_id: str
    title: str
    description: Optional[str] = None
    department: str
    language: str
    status: DocumentStatus
    effective_date: Optional[date] = None
    next_review_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    document_type: Optional[DocumentTypeResponse] = None
    owner_id: int
    versions: Optional[List[DocumentVersionSummary]] = None
    products: Optional[List[ProductResponse]] = None

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Schema for paginated document list."""
    items: List[DocumentResponse]
    total: int
    page: int
    size: int
    pages: int


class DocumentWizardRequest(BaseModel):
    """Schema for document creation wizard."""
    document_type_id: int
    product_ids: Optional[List[int]] = None
    department: str
    language: str = "DE"
    title: str
    description: Optional[str] = None
    template_id: Optional[int] = None
    initial_content: Optional[dict] = None
