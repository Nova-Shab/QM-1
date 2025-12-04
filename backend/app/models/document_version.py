"""
Document version model for versioning and change control.
"""
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class VersionStatus(str, enum.Enum):
    """Version-specific status."""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    EFFECTIVE = "effective"
    SUPERSEDED = "superseded"
    OBSOLETE = "obsolete"


class DocumentVersion(Base):
    """
    Document version entity - represents a specific version of a document.

    Version numbering:
    - Major version: Significant changes requiring full review (1.0, 2.0, 3.0)
    - Minor version: Small corrections, formatting (1.1, 1.2, 2.1)

    Each new version is created from the previous approved version.
    When a new version is approved, the previous becomes 'superseded'.
    """
    __tablename__ = "document_versions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)

    # Version numbering
    version_major = Column(Integer, nullable=False, default=1)
    version_minor = Column(Integer, nullable=False, default=0)

    @property
    def version_label(self):
        """Human-readable version label like '1.0', '2.1'."""
        return f"{self.version_major}.{self.version_minor}"

    # Status
    status = Column(Enum(VersionStatus), default=VersionStatus.DRAFT)

    # Content (stored as JSON for flexibility - could be Markdown, structured data, etc.)
    content = Column(JSON, nullable=True)
    content_text = Column(Text, nullable=True)  # Plain text for full-text search

    # File reference (for documents stored as files)
    file_path = Column(String(500), nullable=True)
    file_name = Column(String(255), nullable=True)

    # Change tracking
    change_summary = Column(Text, nullable=True)
    change_reason = Column(Text, nullable=True)
    related_change_control_id = Column(String(100), nullable=True)  # CC-XXXX
    related_deviation_id = Column(String(100), nullable=True)  # DEV-XXXX
    related_capa_id = Column(String(100), nullable=True)  # CAPA-XXXX

    # Supersession tracking
    superseded_by_version_id = Column(Integer, ForeignKey("document_versions.id"), nullable=True)

    # Authorship
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    effective_at = Column(DateTime, nullable=True)
    superseded_at = Column(DateTime, nullable=True)

    # Relationships
    document = relationship("Document", back_populates="versions")
    created_by = relationship("User", foreign_keys=[created_by_id])
    superseded_by = relationship("DocumentVersion", remote_side=[id], foreign_keys=[superseded_by_version_id])
    approvals = relationship("Approval", back_populates="document_version")
    training_tasks = relationship("TrainingTask", back_populates="document_version")

    @property
    def file_path_full(self):
        """
        Compute the full file path for this version.
        Format: /{department}/{document_type_code}/{document_id}/V{version_label}/
        """
        if self.document:
            return f"{self.document.file_path_base}V{self.version_label}/"
        return None

    def __repr__(self):
        return f"<DocumentVersion(id={self.id}, version={self.version_label}, status={self.status})>"
