"""
Pydantic schemas for API request/response validation.
"""
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLogin,
    Token,
    TokenPayload,
)
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.schemas.document_type import DocumentTypeCreate, DocumentTypeUpdate, DocumentTypeResponse
from app.schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentListResponse,
    DocumentWizardRequest,
)
from app.schemas.document_version import (
    DocumentVersionCreate,
    DocumentVersionUpdate,
    DocumentVersionResponse,
    NewVersionRequest,
)
from app.schemas.approval import ApprovalCreate, ApprovalResponse, ApprovalDecisionRequest
from app.schemas.audit_log import AuditLogResponse
from app.schemas.template import TemplateCreate, TemplateUpdate, TemplateResponse

__all__ = [
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    "Token",
    "TokenPayload",
    # Product
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    # DocumentType
    "DocumentTypeCreate",
    "DocumentTypeUpdate",
    "DocumentTypeResponse",
    # Document
    "DocumentCreate",
    "DocumentUpdate",
    "DocumentResponse",
    "DocumentListResponse",
    "DocumentWizardRequest",
    # DocumentVersion
    "DocumentVersionCreate",
    "DocumentVersionUpdate",
    "DocumentVersionResponse",
    "NewVersionRequest",
    # Approval
    "ApprovalCreate",
    "ApprovalResponse",
    "ApprovalDecisionRequest",
    # AuditLog
    "AuditLogResponse",
    # Template
    "TemplateCreate",
    "TemplateUpdate",
    "TemplateResponse",
]
