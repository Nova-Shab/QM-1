"""
Training task model for Read & Understand workflow.
"""
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class TrainingStatus(str, enum.Enum):
    """Training task status."""
    PENDING = "pending"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    EXEMPT = "exempt"


class TrainingTask(Base):
    """
    Training task entity for Read & Understand workflow.

    When a document is approved/made effective, training tasks are
    created for relevant users based on their role/department.

    Users must confirm they have read and understood the document.
    This is a GxP requirement for document control.
    """
    __tablename__ = "training_tasks"

    id = Column(Integer, primary_key=True, index=True)

    # What needs to be read
    document_version_id = Column(Integer, ForeignKey("document_versions.id"), nullable=False)

    # Who needs to read it
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Status
    status = Column(Enum(TrainingStatus), default=TrainingStatus.PENDING)

    # Completion details
    completed_at = Column(DateTime, nullable=True)
    completion_comment = Column(Text, nullable=True)

    # Due date for training
    due_date = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    document_version = relationship("DocumentVersion", back_populates="training_tasks")
    user = relationship("User", back_populates="training_tasks")

    def __repr__(self):
        return f"<TrainingTask(id={self.id}, user_id={self.user_id}, status={self.status})>"
