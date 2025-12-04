"""
Document version schemas for API validation.
"""
from datetime import datetime
from typing import Optional, Any, List
from pydantic import BaseModel

from app.models.document_version import VersionStatus


class DocumentVersionBase(BaseModel):
    """Base document version schema."""
    content: Optional[dict] = None
    content_text: Optional[str] = None
    change_summary: Optional[str] = None
    change_reason: Optional[str] = None
    related_change_control_id: Optional[str] = None
    related_deviation_id: Optional[str] = None
    related_capa_id: Optional[str] = None


class DocumentVersionCreate(DocumentVersionBase):
    """Schema for creating a new document version."""
    document_id: int


class DocumentVersionUpdate(BaseModel):
    """Schema for updating a document version."""
    content: Optional[dict] = None
    content_text: Optional[str] = None
    change_summary: Optional[str] = None
    change_reason: Optional[str] = None
    related_change_control_id: Optional[str] = None
    related_deviation_id: Optional[str] = None
    related_capa_id: Optional[str] = None


class ApprovalSummary(BaseModel):
    """Summary of an approval for version details."""
    id: int
    approver_name: str
    approval_role: str
    decision: str
    comment: Optional[str] = None
    decided_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentVersionResponse(BaseModel):
    """Schema for document version response."""
    id: int
    document_id: int
    version_major: int
    version_minor: int
    version_label: str
    status: VersionStatus
    content: Optional[dict] = None
    content_text: Optional[str] = None
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    change_summary: Optional[str] = None
    change_reason: Optional[str] = None
    related_change_control_id: Optional[str] = None
    related_deviation_id: Optional[str] = None
    related_capa_id: Optional[str] = None
    created_by_id: int
    created_at: datetime
    updated_at: datetime
    approved_at: Optional[datetime] = None
    effective_at: Optional[datetime] = None
    superseded_at: Optional[datetime] = None
    superseded_by_version_id: Optional[int] = None
    approvals: Optional[List[ApprovalSummary]] = None
    file_path_full: Optional[str] = None

    class Config:
        from_attributes = True


class NewVersionRequest(BaseModel):
    """Schema for creating a new version from existing."""
    is_major: bool = False  # True for major version increment (1.0 -> 2.0)
    change_reason: str
    change_summary: Optional[str] = None
    related_change_control_id: Optional[str] = None
    related_deviation_id: Optional[str] = None
    related_capa_id: Optional[str] = None
