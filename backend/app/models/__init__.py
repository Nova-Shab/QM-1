"""
SQLAlchemy database models for Pharma DMS.
"""
from app.models.user import User, UserRole
from app.models.product import Product, DosageForm, MarketStatus
from app.models.document_type import DocumentType
from app.models.document import Document, DocumentStatus
from app.models.document_version import DocumentVersion, VersionStatus
from app.models.document_product_link import DocumentProductLink
from app.models.approval import Approval, ApprovalDecision, ApprovalRole
from app.models.audit_log import AuditLog
from app.models.template import Template
from app.models.training_task import TrainingTask, TrainingStatus

__all__ = [
    "User",
    "UserRole",
    "Product",
    "DosageForm",
    "MarketStatus",
    "DocumentType",
    "Document",
    "DocumentStatus",
    "DocumentVersion",
    "VersionStatus",
    "DocumentProductLink",
    "Approval",
    "ApprovalDecision",
    "ApprovalRole",
    "AuditLog",
    "Template",
    "TrainingTask",
    "TrainingStatus",
]
