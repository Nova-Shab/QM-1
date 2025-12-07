"""
Document API endpoints.
"""
import json
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.document import Document, DocumentStatus
from app.models.document_version import DocumentVersion, VersionStatus
from app.models.document_type import DocumentType
from app.models.document_product_link import DocumentProductLink
from app.models.product import Product
from app.models.user import User
from app.schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentListResponse,
    DocumentWizardRequest,
    DocumentVersionSummary,
)
from app.schemas.product import ProductResponse
from app.schemas.document_type import DocumentTypeResponse
from app.api.deps import get_current_user, get_author_or_above
from app.services.audit import create_audit_log
from app.services.document import create_document_from_wizard
from app.services.pdf_export import pdf_generator

router = APIRouter(prefix="/documents", tags=["Documents"])


def build_document_response(document: Document) -> DocumentResponse:
    """Build a complete document response with related data."""
    versions = []
    if document.versions:
        for v in document.versions:
            versions.append(DocumentVersionSummary(
                id=v.id,
                version_major=v.version_major,
                version_minor=v.version_minor,
                status=v.status.value,
                created_at=v.created_at
            ))

    products = []
    if document.product_links:
        for link in document.product_links:
            if link.product:
                products.append(ProductResponse.model_validate(link.product))

    doc_type = None
    if document.document_type:
        doc_type = DocumentTypeResponse.model_validate(document.document_type)

    return DocumentResponse(
        id=document.id,
        document_id=document.document_id,
        title=document.title,
        description=document.description,
        department=document.department,
        language=document.language,
        status=document.status,
        effective_date=document.effective_date,
        next_review_date=document.next_review_date,
        created_at=document.created_at,
        updated_at=document.updated_at,
        document_type=doc_type,
        owner_id=document.owner_id,
        versions=versions,
        products=products
    )


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status_filter: Optional[DocumentStatus] = Query(None, alias="status"),
    document_type_id: Optional[int] = None,
    department: Optional[str] = None,
    product_id: Optional[int] = None,
    owner_id: Optional[int] = None,
    review_due_days: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List documents with filtering and pagination.

    Filters:
    - search: Search in title and description
    - status: Filter by document status
    - document_type_id: Filter by document type
    - department: Filter by department
    - product_id: Filter by linked product
    - owner_id: Filter by document owner
    - review_due_days: Filter documents with review due within N days
    """
    query = select(Document).options(
        selectinload(Document.document_type),
        selectinload(Document.versions),
        selectinload(Document.product_links).selectinload(DocumentProductLink.product)
    )

    # Apply filters
    if search:
        query = query.where(
            or_(
                Document.title.ilike(f"%{search}%"),
                Document.description.ilike(f"%{search}%"),
                Document.document_id.ilike(f"%{search}%")
            )
        )

    if status_filter:
        query = query.where(Document.status == status_filter)

    if document_type_id:
        query = query.where(Document.document_type_id == document_type_id)

    if department:
        query = query.where(Document.department == department)

    if owner_id:
        query = query.where(Document.owner_id == owner_id)

    if product_id:
        query = query.join(DocumentProductLink).where(DocumentProductLink.product_id == product_id)

    if review_due_days:
        from datetime import timedelta
        due_date = date.today() + timedelta(days=review_due_days)
        query = query.where(Document.next_review_date <= due_date)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar() or 0

    # Apply pagination
    offset = (page - 1) * size
    query = query.order_by(Document.updated_at.desc()).offset(offset).limit(size)

    result = await db.execute(query)
    documents = result.scalars().unique().all()

    # Build response
    items = [build_document_response(doc) for doc in documents]
    pages = (total + size - 1) // size

    return DocumentListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific document by ID."""
    query = select(Document).where(Document.id == document_id).options(
        selectinload(Document.document_type),
        selectinload(Document.versions),
        selectinload(Document.product_links).selectinload(DocumentProductLink.product)
    )

    result = await db.execute(query)
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    return build_document_response(document)


@router.post("/wizard", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document_wizard(
    wizard_data: DocumentWizardRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_author_or_above)
):
    """
    Create a new document using the document creation wizard.

    The wizard:
    1. Generates a unique document ID based on department and type
    2. Creates the document with initial metadata
    3. Creates the first version (v1.0) in draft status
    4. Links specified products
    5. Applies template structure if specified
    """
    try:
        document = await create_document_from_wizard(
            db=db,
            document_type_id=wizard_data.document_type_id,
            department=wizard_data.department,
            language=wizard_data.language,
            title=wizard_data.title,
            description=wizard_data.description,
            created_by=current_user,
            product_ids=wizard_data.product_ids,
            template_id=wizard_data.template_id,
            initial_content=wizard_data.initial_content
        )
        await db.commit()

        # Reload with relationships
        query = select(Document).where(Document.id == document.id).options(
            selectinload(Document.document_type),
            selectinload(Document.versions),
            selectinload(Document.product_links).selectinload(DocumentProductLink.product)
        )
        result = await db.execute(query)
        document = result.scalar_one()

        return build_document_response(document)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    document_data: DocumentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_author_or_above)
):
    """Update document metadata."""
    query = select(Document).where(Document.id == document_id).options(
        selectinload(Document.document_type),
        selectinload(Document.versions),
        selectinload(Document.product_links).selectinload(DocumentProductLink.product)
    )

    result = await db.execute(query)
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Check if user is owner or has elevated permissions
    if document.owner_id != current_user.id and current_user.role not in ["admin", "qa_approver", "qp"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this document"
        )

    update_data = document_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(document, field, value)

    await db.commit()
    await db.refresh(document)

    await create_audit_log(
        db=db,
        entity_type="Document",
        entity_id=document.id,
        action="update",
        performed_by_id=current_user.id,
        details={"updated_fields": list(update_data.keys())}
    )

    return build_document_response(document)


@router.post("/{document_id}/submit-for-review", response_model=DocumentResponse)
async def submit_for_review(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_author_or_above)
):
    """Submit a document for review (Draft -> InReview)."""
    query = select(Document).where(Document.id == document_id).options(
        selectinload(Document.document_type),
        selectinload(Document.versions),
        selectinload(Document.product_links).selectinload(DocumentProductLink.product)
    )

    result = await db.execute(query)
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    if document.status != DocumentStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot submit for review: document is in '{document.status}' status"
        )

    # Update document status
    old_status = document.status
    document.status = DocumentStatus.IN_REVIEW

    # Update latest version status
    if document.versions:
        latest_version = document.versions[0]  # Already ordered by desc
        if latest_version.status == VersionStatus.DRAFT:
            latest_version.status = VersionStatus.IN_REVIEW

    await db.commit()
    await db.refresh(document)

    await create_audit_log(
        db=db,
        entity_type="Document",
        entity_id=document.id,
        action="status_change",
        performed_by_id=current_user.id,
        details={
            "old_status": old_status.value,
            "new_status": document.status.value
        },
        description=f"Document {document.document_id} submitted for review"
    )

    return build_document_response(document)


@router.get("/{document_id}/export/pdf")
async def export_document_pdf(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export a document as PDF.

    Generates a professional PDF document including:
    - Document metadata (ID, version, status)
    - All document content sections
    - Approval signature blocks
    - Company header and footer
    """
    # Get document with all relationships
    query = select(Document).where(Document.id == document_id).options(
        selectinload(Document.document_type),
        selectinload(Document.versions),
        selectinload(Document.owner)
    )

    result = await db.execute(query)
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Get current version content
    current_version = None
    version_number = "1.0"
    content = {}

    if document.versions:
        for v in document.versions:
            if v.is_current:
                current_version = v
                break
        if not current_version:
            current_version = document.versions[0]

        version_number = f"{current_version.version_major}.{current_version.version_minor}"

        if current_version.content:
            try:
                content = json.loads(current_version.content) if isinstance(current_version.content, str) else current_version.content
            except json.JSONDecodeError:
                content = {"content": current_version.content}

    # Get owner name
    owner_name = document.owner.name if document.owner else "Unknown"

    # Get document type name
    doc_type_name = document.document_type.name_de if document.document_type else "Dokument"

    # Generate PDF
    pdf_bytes = pdf_generator.generate_document_pdf(
        document_id=document.document_id,
        title=document.title,
        document_type=doc_type_name,
        department=document.department or "Allgemein",
        version=version_number,
        status=document.status.value,
        owner=owner_name,
        effective_date=document.effective_date,
        review_date=document.next_review_date,
        content=content,
        created_at=document.created_at,
    )

    # Log the export
    await create_audit_log(
        db=db,
        entity_type="Document",
        entity_id=document.id,
        action="export_pdf",
        performed_by_id=current_user.id,
        details={"version": version_number},
        description=f"Document {document.document_id} exported as PDF"
    )

    # Create safe filename
    safe_filename = f"{document.document_id}_{version_number}.pdf".replace(" ", "_").replace("/", "-")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_filename}"'
        }
    )
