"""
Approval schemas for API validation.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.models.approval import ApprovalDecision, ApprovalRole


class ApprovalBase(BaseModel):
    """Base approval schema."""
    approval_role: ApprovalRole
    comment: Optional[str] = None


class ApprovalCreate(ApprovalBase):
    """Schema for creating a new approval."""
    document_version_id: int


class ApprovalDecisionRequest(BaseModel):
    """Schema for making an approval decision."""
    decision: ApprovalDecision
    comment: Optional[str] = None


class ApprovalResponse(BaseModel):
    """Schema for approval response."""
    id: int
    document_version_id: int
    approver_id: int
    approver_name: str
    approval_role: ApprovalRole
    decision: ApprovalDecision
    comment: Optional[str] = None
    sequence_number: int
    requested_at: datetime
    decided_at: Optional[datetime] = None

    class Config:
        from_attributes = True
