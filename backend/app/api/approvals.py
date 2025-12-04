"""
Approval workflow API endpoints.
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
from app.models.document_type import DocumentType
from app.models.approval import Approval, ApprovalDecision, ApprovalRole
from app.models.user import User, UserRole
from app.schemas.approval import ApprovalCreate, ApprovalResponse, ApprovalDecisionRequest
from app.api.deps import get_current_user, get_reviewer_or_above, get_approver_or_above
from app.services.audit import create_audit_log, format_approval_description

router = APIRouter(prefix="/approvals", tags=["Approvals"])


def get_approval_role_from_user_role(user_role: UserRole) -> ApprovalRole:
    """Map user role to approval role."""
    mapping = {
        UserRole.ADMIN: ApprovalRole.QA_APPROVER,
        UserRole.AUTHOR: ApprovalRole.AUTHOR,
        UserRole.QA_REVIEWER: ApprovalRole.QA_REVIEWER,
        UserRole.QA_APPROVER: ApprovalRole.QA_APPROVER,
        UserRole.QP: ApprovalRole.QP,
        UserRole.RA: ApprovalRole.RA,
    }
    return mapping.get(user_role, ApprovalRole.AUTHOR)


@router.get("/version/{version_id}", response_model=List[ApprovalResponse])
async def list_approvals(
    version_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all approvals for a document version."""
    query = select(Approval).where(
        Approval.document_version_id == version_id
    ).options(
        selectinload(Approval.approver)
    ).order_by(Approval.sequence_number)

    result = await db.execute(query)
    approvals = result.scalars().all()

    responses = []
    for a in approvals:
        responses.append(ApprovalResponse(
            id=a.id,
            document_version_id=a.document_version_id,
            approver_id=a.approver_id,
            approver_name=a.approver.name if a.approver else "Unknown",
            approval_role=a.approval_role,
            decision=a.decision,
            comment=a.comment,
            sequence_number=a.sequence_number,
            requested_at=a.requested_at,
            decided_at=a.decided_at
        ))

    return responses


@router.post("/version/{version_id}/review", response_model=ApprovalResponse)
async def review_version(
    version_id: int,
    decision_data: ApprovalDecisionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_reviewer_or_above)
):
    """
    Submit a review decision for a document version.

    This is used by QA reviewers to review documents.
    """
    # Get version with document
    query = select(DocumentVersion).where(DocumentVersion.id == version_id).options(
        selectinload(DocumentVersion.document).selectinload(Document.document_type)
    )
    result = await db.execute(query)
    version = result.scalar_one_or_none()

    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    if version.status != VersionStatus.IN_REVIEW:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot review: version is in '{version.status}' status"
        )

    # Get the count of existing approvals for sequence number
    result = await db.execute(
        select(Approval).where(Approval.document_version_id == version_id)
    )
    existing_approvals = result.scalars().all()
    sequence_number = len(existing_approvals) + 1

    # Create approval record
    approval_role = get_approval_role_from_user_role(current_user.role)
    approval = Approval(
        document_version_id=version_id,
        approver_id=current_user.id,
        approval_role=approval_role,
        decision=decision_data.decision,
        comment=decision_data.comment,
        sequence_number=sequence_number,
        decided_at=datetime.utcnow()
    )
    db.add(approval)

    # Handle decision
    if decision_data.decision == ApprovalDecision.REJECTED:
        # Rejection: send back to draft
        version.status = VersionStatus.DRAFT
        version.document.status = DocumentStatus.DRAFT
    elif decision_data.decision == ApprovalDecision.APPROVED:
        # Check if QP approval is required
        doc_type = version.document.document_type
        if doc_type and doc_type.requires_qp_approval:
            # Need QP approval next - keep in review
            pass
        else:
            # No QP required - this review approves the document
            # But we still need final QA approval step
            pass

    await db.commit()
    await db.refresh(approval)

    # Create audit log
    await create_audit_log(
        db=db,
        entity_type="DocumentVersion",
        entity_id=version_id,
        action="review",
        performed_by_id=current_user.id,
        details={
            "decision": decision_data.decision.value,
            "comment": decision_data.comment,
            "role": approval_role.value
        },
        description=format_approval_description(
            "Document", version.document.document_id,
            decision_data.decision.value, approval_role.value, current_user.name
        )
    )

    return ApprovalResponse(
        id=approval.id,
        document_version_id=approval.document_version_id,
        approver_id=approval.approver_id,
        approver_name=current_user.name,
        approval_role=approval.approval_role,
        decision=approval.decision,
        comment=approval.comment,
        sequence_number=approval.sequence_number,
        requested_at=approval.requested_at,
        decided_at=approval.decided_at
    )


@router.post("/version/{version_id}/approve", response_model=ApprovalResponse)
async def approve_version(
    version_id: int,
    decision_data: ApprovalDecisionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_approver_or_above)
):
    """
    Submit final approval for a document version.

    This is the final approval step that makes the document Approved/Effective.
    Required role: QA_APPROVER, QP, or ADMIN.
    """
    # Get version with document and type
    query = select(DocumentVersion).where(DocumentVersion.id == version_id).options(
        selectinload(DocumentVersion.document).selectinload(Document.document_type),
        selectinload(DocumentVersion.approvals)
    )
    result = await db.execute(query)
    version = result.scalar_one_or_none()

    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    if version.status != VersionStatus.IN_REVIEW:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot approve: version is in '{version.status}' status"
        )

    document = version.document
    doc_type = document.document_type

    # Check if QP approval is specifically required
    if doc_type and doc_type.requires_qp_approval:
        if current_user.role != UserRole.QP and current_user.role != UserRole.ADMIN:
            # Check if there's already a QP approval
            has_qp_approval = any(
                a.approval_role == ApprovalRole.QP and a.decision == ApprovalDecision.APPROVED
                for a in version.approvals
            )
            if not has_qp_approval:
                raise HTTPException(
                    status_code=403,
                    detail="This document type requires QP (Qualified Person) approval"
                )

    # Get sequence number
    sequence_number = len(version.approvals) + 1

    # Create approval record
    approval_role = ApprovalRole.QP if current_user.role == UserRole.QP else ApprovalRole.QA_APPROVER
    approval = Approval(
        document_version_id=version_id,
        approver_id=current_user.id,
        approval_role=approval_role,
        decision=decision_data.decision,
        comment=decision_data.comment,
        sequence_number=sequence_number,
        decided_at=datetime.utcnow()
    )
    db.add(approval)

    # Handle decision
    if decision_data.decision == ApprovalDecision.REJECTED:
        # Rejection: send back to draft
        version.status = VersionStatus.DRAFT
        document.status = DocumentStatus.DRAFT
    elif decision_data.decision == ApprovalDecision.APPROVED:
        # Final approval: mark as approved/effective
        now = datetime.utcnow()

        # Supersede any previous effective version
        result = await db.execute(
            select(DocumentVersion).where(
                DocumentVersion.document_id == document.id,
                DocumentVersion.status.in_([VersionStatus.EFFECTIVE, VersionStatus.APPROVED]),
                DocumentVersion.id != version_id
            )
        )
        previous_versions = result.scalars().all()
        for prev in previous_versions:
            prev.status = VersionStatus.SUPERSEDED
            prev.superseded_at = now
            prev.superseded_by_version_id = version_id

        # Update version status
        version.status = VersionStatus.EFFECTIVE
        version.approved_at = now
        version.effective_at = now

        # Update document status
        document.status = DocumentStatus.EFFECTIVE
        document.effective_date = now.date()

    await db.commit()
    await db.refresh(approval)

    # Create audit log
    await create_audit_log(
        db=db,
        entity_type="DocumentVersion",
        entity_id=version_id,
        action="approval",
        performed_by_id=current_user.id,
        details={
            "decision": decision_data.decision.value,
            "comment": decision_data.comment,
            "role": approval_role.value,
            "final_status": version.status.value
        },
        description=format_approval_description(
            "Document", document.document_id,
            decision_data.decision.value, approval_role.value, current_user.name
        )
    )

    return ApprovalResponse(
        id=approval.id,
        document_version_id=approval.document_version_id,
        approver_id=approval.approver_id,
        approver_name=current_user.name,
        approval_role=approval.approval_role,
        decision=approval.decision,
        comment=approval.comment,
        sequence_number=approval.sequence_number,
        requested_at=approval.requested_at,
        decided_at=approval.decided_at
    )


@router.get("/pending", response_model=List[ApprovalResponse])
async def get_pending_approvals(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_reviewer_or_above)
):
    """Get all pending approvals (documents in review)."""
    # Get all versions in review that don't have a final approval
    query = select(DocumentVersion).where(
        DocumentVersion.status == VersionStatus.IN_REVIEW
    ).options(
        selectinload(DocumentVersion.document),
        selectinload(DocumentVersion.approvals).selectinload(Approval.approver)
    )

    result = await db.execute(query)
    versions = result.scalars().all()

    # Create pending approval entries for each version
    pending = []
    for version in versions:
        # Check if this user can still approve
        user_already_approved = any(
            a.approver_id == current_user.id
            for a in version.approvals
        )

        if not user_already_approved:
            pending.append(ApprovalResponse(
                id=0,  # Placeholder - not a real approval yet
                document_version_id=version.id,
                approver_id=current_user.id,
                approver_name=current_user.name,
                approval_role=get_approval_role_from_user_role(current_user.role),
                decision=ApprovalDecision.PENDING,
                comment=None,
                sequence_number=len(version.approvals) + 1,
                requested_at=version.updated_at,
                decided_at=None
            ))

    return pending
