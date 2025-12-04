"""
Audit log model for GxP compliance.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class AuditLog(Base):
    """
    Audit log entity for tracking all system changes.

    GxP Requirement: Complete audit trail for:
    - Document creation, modification, deletion
    - Status changes
    - Approval actions
    - User actions

    This log is append-only - entries cannot be modified or deleted.
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    # What was affected
    entity_type = Column(String(100), nullable=False, index=True)  # Document, DocumentVersion, etc.
    entity_id = Column(Integer, nullable=False, index=True)

    # What happened
    action = Column(String(100), nullable=False, index=True)  # create, update, status_change, approval, etc.

    # Who did it
    performed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # When
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Details (JSON for flexibility)
    details = Column(JSON, nullable=True)

    # Human-readable description
    description = Column(Text, nullable=True)

    # IP address for security audit
    ip_address = Column(String(50), nullable=True)

    # Relationships
    performed_by_user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, entity={self.entity_type}:{self.entity_id}, action={self.action})>"
