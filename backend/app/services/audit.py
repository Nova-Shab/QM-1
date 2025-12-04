"""
Audit logging service for GxP compliance.
"""
from typing import Optional, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


async def create_audit_log(
    db: AsyncSession,
    entity_type: str,
    entity_id: int,
    action: str,
    performed_by_id: int,
    details: Optional[dict] = None,
    description: Optional[str] = None,
    ip_address: Optional[str] = None
) -> AuditLog:
    """
    Create an audit log entry.

    This function is called for all significant actions in the system
    to maintain a complete audit trail for GxP compliance.

    Args:
        db: Database session
        entity_type: Type of entity (Document, DocumentVersion, Product, etc.)
        entity_id: ID of the affected entity
        action: Action performed (create, update, status_change, approval, etc.)
        performed_by_id: User ID who performed the action
        details: Additional details as JSON
        description: Human-readable description
        ip_address: Client IP address for security audit

    Returns:
        Created AuditLog entry
    """
    audit_log = AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        performed_by_id=performed_by_id,
        timestamp=datetime.utcnow(),
        details=details,
        description=description,
        ip_address=ip_address
    )
    db.add(audit_log)
    # Note: We don't commit here - let the caller manage the transaction
    return audit_log


def format_status_change_description(
    entity_type: str,
    entity_id: str,
    old_status: str,
    new_status: str
) -> str:
    """Format a human-readable description for status changes."""
    return f"{entity_type} {entity_id}: Status changed from '{old_status}' to '{new_status}'"


def format_approval_description(
    entity_type: str,
    entity_id: str,
    decision: str,
    role: str,
    approver_name: str
) -> str:
    """Format a human-readable description for approval actions."""
    return f"{entity_type} {entity_id}: {decision.capitalize()} by {approver_name} ({role})"
