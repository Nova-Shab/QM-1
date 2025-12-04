"""
Document model - the main entity for document management.
"""
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, Text, ForeignKey, Date
from sqlalchemy.orm import relationship

from app.core.database import Base


class DocumentStatus(str, enum.Enum):
    """Document lifecycle status."""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    EFFECTIVE = "effective"
    OBSOLETE = "obsolete"
    ARCHIVED = "archived"


class Document(Base):
    """
    Document entity - represents a document throughout its lifecycle.

    A Document can have multiple versions (DocumentVersion).
    The Document holds the common metadata, while each version
    holds the actual content and version-specific data.

    Document ID format: {DEPT}-{DOCTYPE}-{NUMBER}
    Example: QA-SOP-0001, REG-FI-0005, PROD-WI-0012
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    # Human-readable document identifier
    document_id = Column(String(100), unique=True, nullable=False, index=True)

    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)

    # Classification
    document_type_id = Column(Integer, ForeignKey("document_types.id"), nullable=False)
    department = Column(String(100), nullable=False)
    language = Column(String(10), default="DE")  # DE, EN, etc.

    # Ownership
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Status tracking
    status = Column(Enum(DocumentStatus), default=DocumentStatus.DRAFT)
    effective_date = Column(Date, nullable=True)
    next_review_date = Column(Date, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    document_type = relationship("DocumentType", back_populates="documents")
    owner = relationship("User", back_populates="owned_documents")
    versions = relationship("DocumentVersion", back_populates="document", order_by="desc(DocumentVersion.created_at)")
    product_links = relationship("DocumentProductLink", back_populates="document")

    @property
    def current_version(self):
        """Get the current effective or latest approved version."""
        for version in self.versions:
            if version.status in ["effective", "approved"]:
                return version
        # Return latest draft if no approved version exists
        return self.versions[0] if self.versions else None

    @property
    def file_path_base(self):
        """
        Compute the base file path for this document.
        Format: /{department}/{document_type_code}/{document_id}/
        """
        doc_type_code = self.document_type.code if self.document_type else "UNKNOWN"
        return f"/{self.department}/{doc_type_code}/{self.document_id}/"

    def __repr__(self):
        return f"<Document(id={self.id}, document_id='{self.document_id}', status={self.status})>"
