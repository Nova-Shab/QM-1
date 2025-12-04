"""
Approval model for review and approval workflow.
"""
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class ApprovalDecision(str, enum.Enum):
    """Approval decision options."""
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"


class ApprovalRole(str, enum.Enum):
    """Role in the approval workflow."""
    AUTHOR = "author"  # Document author submitting for review
    QA_REVIEWER = "qa_reviewer"  # QA reviewing the document
    QA_APPROVER = "qa_approver"  # QA approving the document
    QP = "qp"  # Qualified Person (Sachkundige Person)
    DEPARTMENT_HEAD = "department_head"  # Department head approval
    RA = "ra"  # Regulatory Affairs approval


class Approval(Base):
    """
    Approval entity for tracking document approval workflow.

    Each approval represents a step in the approval process:
    1. Author submits document (AUTHOR role, APPROVED decision)
    2. QA reviews document (QA_REVIEWER role)
    3. QA approves document (QA_APPROVER role)
    4. If required: QP approves document (QP role)

    Rejections send the document back to draft status.
    """
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True)
    document_version_id = Column(Integer, ForeignKey("document_versions.id"), nullable=False)
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Workflow information
    approval_role = Column(Enum(ApprovalRole), nullable=False)
    decision = Column(Enum(ApprovalDecision), default=ApprovalDecision.PENDING)
    comment = Column(Text, nullable=True)

    # Sequence in workflow (1 = first approval step, 2 = second, etc.)
    sequence_number = Column(Integer, default=1)

    # Timestamps
    requested_at = Column(DateTime, default=datetime.utcnow)
    decided_at = Column(DateTime, nullable=True)

    # Relationships
    document_version = relationship("DocumentVersion", back_populates="approvals")
    approver = relationship("User", back_populates="approvals")

    def __repr__(self):
        return f"<Approval(id={self.id}, role={self.approval_role}, decision={self.decision})>"
