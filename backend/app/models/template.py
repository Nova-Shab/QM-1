"""
Template model for document creation wizard.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base


class Template(Base):
    """
    Template entity for automatic document creation.

    Templates define the structure and default content for different
    document types. The document wizard uses templates to generate
    new documents with pre-filled sections.

    Structure definition example for an SOP:
    {
        "sections": [
            {"id": "purpose", "title": "1. Purpose / Zweck", "required": true},
            {"id": "scope", "title": "2. Scope / Geltungsbereich", "required": true},
            {"id": "responsibilities", "title": "3. Responsibilities / Verantwortlichkeiten", "required": true},
            {"id": "definitions", "title": "4. Definitions / Definitionen", "required": false},
            {"id": "procedure", "title": "5. Procedure / Verfahren", "required": true},
            {"id": "records", "title": "6. Records / Aufzeichnungen", "required": true},
            {"id": "references", "title": "7. References / Referenzen", "required": false},
            {"id": "attachments", "title": "8. Attachments / Anlagen", "required": false},
            {"id": "history", "title": "9. Document History / Dokumentenhistorie", "required": true}
        ]
    }
    """
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)

    # Link to document type
    document_type_id = Column(Integer, ForeignKey("document_types.id"), nullable=False)

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    language = Column(String(10), default="DE")

    # Template structure (JSON defining sections, fields, etc.)
    structure_definition = Column(JSON, nullable=True)

    # Default content (Markdown or HTML)
    default_content = Column(Text, nullable=True)

    # Patterns for auto-generating document metadata
    default_title_pattern = Column(String(500), nullable=True)  # e.g., "SOP: {{process_name}}"
    default_document_id_pattern = Column(String(100), nullable=True)  # e.g., "{{dept}}-SOP-{{number}}"

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    document_type = relationship("DocumentType", back_populates="templates")

    def __repr__(self):
        return f"<Template(id={self.id}, name='{self.name}')>"
