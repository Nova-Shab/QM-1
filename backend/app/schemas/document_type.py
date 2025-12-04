"""
Document type schemas for API validation.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DocumentTypeBase(BaseModel):
    """Base document type schema."""
    code: str
    name: str
    name_de: Optional[str] = None
    description: Optional[str] = None
    gxp_relevant: bool = True
    requires_qp_approval: bool = False
    default_review_period_months: int = 24
    category: Optional[str] = None


class DocumentTypeCreate(DocumentTypeBase):
    """Schema for creating a new document type."""
    pass


class DocumentTypeUpdate(BaseModel):
    """Schema for updating a document type."""
    name: Optional[str] = None
    name_de: Optional[str] = None
    description: Optional[str] = None
    gxp_relevant: Optional[bool] = None
    requires_qp_approval: Optional[bool] = None
    default_review_period_months: Optional[int] = None
    category: Optional[str] = None


class DocumentTypeResponse(DocumentTypeBase):
    """Schema for document type response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
