"""
Document-Product link model for many-to-many relationship.
"""
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class RelationType(str, enum.Enum):
    """Type of relationship between document and product."""
    PRIMARY = "primary"  # Main product this document is for
    RELATED = "related"  # Document also applies to this product
    REFERENCE = "reference"  # Document references this product


class DocumentProductLink(Base):
    """
    Link table between Document and Product.

    Allows a document to be associated with multiple products
    and tracks the type of relationship.
    """
    __tablename__ = "document_product_links"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    relation_type = Column(Enum(RelationType), default=RelationType.PRIMARY)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="product_links")
    product = relationship("Product", back_populates="document_links")

    def __repr__(self):
        return f"<DocumentProductLink(document_id={self.document_id}, product_id={self.product_id})>"
