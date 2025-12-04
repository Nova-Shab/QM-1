"""
Template schemas for API validation.
"""
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel


class TemplateBase(BaseModel):
    """Base template schema."""
    document_type_id: int
    name: str
    description: Optional[str] = None
    language: str = "DE"
    structure_definition: Optional[dict] = None
    default_content: Optional[str] = None
    default_title_pattern: Optional[str] = None
    default_document_id_pattern: Optional[str] = None
    is_active: bool = True


class TemplateCreate(TemplateBase):
    """Schema for creating a new template."""
    pass


class TemplateUpdate(BaseModel):
    """Schema for updating a template."""
    name: Optional[str] = None
    description: Optional[str] = None
    language: Optional[str] = None
    structure_definition: Optional[dict] = None
    default_content: Optional[str] = None
    default_title_pattern: Optional[str] = None
    default_document_id_pattern: Optional[str] = None
    is_active: Optional[bool] = None


class TemplateResponse(TemplateBase):
    """Schema for template response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
