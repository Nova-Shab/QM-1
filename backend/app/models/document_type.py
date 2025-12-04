"""
Document type model for categorizing documents.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class DocumentType(Base):
    """
    Document type entity for categorizing documents.

    Common GxP document types:
    - SOP: Standard Operating Procedure
    - WI: Work Instruction
    - FORM: Form/Template
    - SPEC: Specification
    - MBR: Master Batch Record
    - BATCH-RECORD: Batch Production Record
    - CERT-GMP: GMP Certificate
    - FI: Fachinformation (SmPC)
    - GI: Gebrauchsinformation (PIL/Package Insert)
    - AC: Analysenzertifikat (Certificate of Analysis)
    - TEST-INST: Test Instruction / Prüfanweisung
    - VAL: Validation Document
    - DEV: Deviation Report
    - CAPA: Corrective and Preventive Action
    - CC: Change Control
    """
    __tablename__ = "document_types"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    name_de = Column(String(255), nullable=True)  # German name
    description = Column(Text, nullable=True)
    gxp_relevant = Column(Boolean, default=True)
    requires_qp_approval = Column(Boolean, default=False)
    default_review_period_months = Column(Integer, default=24)  # Standard review cycle
    category = Column(String(100), nullable=True)  # e.g., "Quality", "Regulatory", "Production"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    documents = relationship("Document", back_populates="document_type")
    templates = relationship("Template", back_populates="document_type")

    def __repr__(self):
        return f"<DocumentType(id={self.id}, code='{self.code}')>"
