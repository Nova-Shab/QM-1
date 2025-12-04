"""
Audit log schemas for API validation.
"""
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    """Schema for audit log response."""
    id: int
    entity_type: str
    entity_id: int
    action: str
    performed_by_id: int
    performed_by_name: Optional[str] = None
    timestamp: datetime
    details: Optional[dict] = None
    description: Optional[str] = None
    ip_address: Optional[str] = None

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    """Schema for paginated audit log list."""
    items: list[AuditLogResponse]
    total: int
    page: int
    size: int
    pages: int
