"""
User model for authentication and authorization.
"""
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserRole(str, enum.Enum):
    """User roles for role-based access control."""
    ADMIN = "admin"
    AUTHOR = "author"
    QA_REVIEWER = "qa_reviewer"
    QA_APPROVER = "qa_approver"
    QP = "qp"  # Qualified Person / Sachkundige Person
    RA = "ra"  # Regulatory Affairs
    PRODUCTION = "production"
    READ_ONLY = "read_only"


class User(Base):
    """
    User entity for authentication and access control.

    Roles determine what actions a user can perform:
    - ADMIN: Full system access
    - AUTHOR: Can create and edit documents
    - QA_REVIEWER: Can review documents
    - QA_APPROVER: Can approve documents for QA
    - QP: Qualified Person, required for certain document approvals
    - RA: Regulatory Affairs
    - PRODUCTION: Production department access
    - READ_ONLY: View-only access
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.READ_ONLY)
    department = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owned_documents = relationship("Document", back_populates="owner")
    approvals = relationship("Approval", back_populates="approver")
    audit_logs = relationship("AuditLog", back_populates="performed_by_user")
    training_tasks = relationship("TrainingTask", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role={self.role})>"
