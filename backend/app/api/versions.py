"""
Document version API endpoints.
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.document import Document, DocumentStatus
from app.models.document_version import DocumentVersion, VersionStatus
from app.models.approval import Approval, ApprovalDecision
from app.models.user import User
from app.schemas.document_version import (
    DocumentVersionCreate,
    DocumentVersionUpdate,
    DocumentVersionResponse,
    NewVersionRequest,
    ApprovalSummary,
)
from app.api.deps import get_current_user, get_author_or_above
from app.services.audit import create_audit_log
from app.services.document import create_new_version, compute_file_path

router = APIRouter(prefix="/versions", tags=["Document Versions"])


def build_version_response(version: DocumentVersion, document: Optional[Document] = None) -> DocumentVersionResponse:
    """Build a complete version response."""
    approvals = []
    if version.approvals:
        for a in version.approvals:
            approver_name = a.approver.name if a.approver else "Unknown"
            approvals.append(ApprovalSummary(
                id=a.id,
                approver_name=approver_name,
                approval_role=a.approval_role.value,
                decision=a.decision.value,
                comment=a.comment,
                decided_at=a.decided_at
            ))

    # Compute file path if document is available
    file_path_full = None
    if document:
        file_path_full = compute_file_path(document, version)

    return DocumentVersionResponse(
        id=version.id,
        document_id=version.document_id,
        version_major=version.version_major,
        version_minor=version.version_minor,
        version_label=f"{version.version_major}.{version.version_minor}",
        status=version.status,
        content=version.content,
        content_text=version.content_text,
        file_path=version.file_path,
        file_name=version.file_name,
        change_summary=version.change_summary,
        change_reason=version.change_reason,
        related_change_control_id=version.related_change_control_id,
        related_deviation_id=version.related_deviation_id,
        related_capa_id=version.related_capa_id,
        created_by_id=version.created_by_id,
        created_at=version.created_at,
        updated_at=version.updated_at,
        approved_at=version.approved_at,
        effective_at=version.effective_at,
        superseded_at=version.superseded_at,
        superseded_by_version_id=version.superseded_by_version_id,
        approvals=approvals,
        file_path_full=file_path_full
    )


@router.get("/document/{document_id}", response_model=List[DocumentVersionResponse])
async def list_versions(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all versions of a document."""
    # Get document
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Get versions
    query = select(DocumentVersion).where(
        DocumentVersion.document_id == document_id
    ).options(
        selectinload(DocumentVersion.approvals).selectinload(Approval.approver)
    ).order_by(DocumentVersion.version_major.desc(), DocumentVersion.version_minor.desc())

    result = await db.execute(query)
    versions = result.scalars().all()

    return [build_version_response(v, document) for v in versions]


@router.get("/{version_id}", response_model=DocumentVersionResponse)
async def get_version(
    version_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific version by ID."""
    query = select(DocumentVersion).where(DocumentVersion.id == version_id).options(
        selectinload(DocumentVersion.approvals).selectinload(Approval.approver),
        selectinload(DocumentVersion.document).selectinload(Document.document_type)
    )

    result = await db.execute(query)
    version = result.scalar_one_or_none()

    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    return build_version_response(version, version.document)


@router.post("/document/{document_id}/new-version", response_model=DocumentVersionResponse, status_code=status.HTTP_201_CREATED)
async def create_version(
    document_id: int,
    request: NewVersionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_author_or_above)
):
    """
    Create a new version of an existing document.

    This copies the content from the current approved version
    and creates a new draft version with incremented version number.
    """
    try:
        version = await create_new_version(
            db=db,
            document_id=document_id,
            created_by=current_user,
            is_major=request.is_major,
            change_reason=request.change_reason,
            change_summary=request.change_summary,
            related_change_control_id=request.related_change_control_id,
            related_deviation_id=request.related_deviation_id,
            related_capa_id=request.related_capa_id
        )
        await db.commit()

        # Reload with relationships
        query = select(DocumentVersion).where(DocumentVersion.id == version.id).options(
            selectinload(DocumentVersion.approvals).selectinload(Approval.approver),
            selectinload(DocumentVersion.document).selectinload(Document.document_type)
        )
        result = await db.execute(query)
        version = result.scalar_one()

        return build_version_response(version, version.document)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{version_id}", response_model=DocumentVersionResponse)
async def update_version(
    version_id: int,
    version_data: DocumentVersionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_author_or_above)
):
    """Update a version's content and metadata (only for draft versions)."""
    query = select(DocumentVersion).where(DocumentVersion.id == version_id).options(
        selectinload(DocumentVersion.approvals).selectinload(Approval.approver),
        selectinload(DocumentVersion.document).selectinload(Document.document_type)
    )

    result = await db.execute(query)
    version = result.scalar_one_or_none()

    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    if version.status != VersionStatus.DRAFT:
        raise HTTPException(
            status_code=400,
            detail="Can only edit draft versions"
        )

    update_data = version_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(version, field, value)

    await db.commit()
    await db.refresh(version)

    await create_audit_log(
        db=db,
        entity_type="DocumentVersion",
        entity_id=version.id,
        action="update",
        performed_by_id=current_user.id,
        details={"updated_fields": list(update_data.keys())}
    )

    return build_version_response(version, version.document)
