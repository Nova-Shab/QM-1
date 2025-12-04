"""
Search and reporting API endpoints.
"""
from typing import List, Optional
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
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
from app.schemas.document import DocumentResponse, DocumentListResponse
from app.api.deps import get_current_user
from app.api.documents import build_document_response

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/documents", response_model=DocumentListResponse)
async def search_documents(
    q: Optional[str] = Query(None, description="Full-text search query"),
    status_filter: Optional[DocumentStatus] = Query(None, alias="status"),
    document_type: Optional[str] = Query(None, description="Document type code"),
    department: Optional[str] = None,
    product: Optional[str] = Query(None, description="Product name or ID"),
    owner: Optional[str] = Query(None, description="Owner name or email"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search documents with full-text search and filtering.

    Query parameter 'q' searches across:
    - Document ID
    - Title
    - Description
    """
    query = select(Document).options(
        selectinload(Document.document_type),
        selectinload(Document.versions),
        selectinload(Document.product_links).selectinload(DocumentProductLink.product),
        selectinload(Document.owner)
    )

    # Full-text search
    if q:
        search_term = f"%{q}%"
        query = query.where(
            or_(
                Document.document_id.ilike(search_term),
                Document.title.ilike(search_term),
                Document.description.ilike(search_term)
            )
        )

    # Status filter
    if status_filter:
        query = query.where(Document.status == status_filter)

    # Document type filter
    if document_type:
        query = query.join(DocumentType).where(DocumentType.code == document_type)

    # Department filter
    if department:
        query = query.where(Document.department == department)

    # Product filter
    if product:
        # Try to parse as ID first
        try:
            product_id = int(product)
            query = query.join(DocumentProductLink).where(DocumentProductLink.product_id == product_id)
        except ValueError:
            # Search by name
            query = query.join(DocumentProductLink).join(Product).where(
                or_(
                    Product.name.ilike(f"%{product}%"),
                    Product.short_name.ilike(f"%{product}%")
                )
            )

    # Owner filter
    if owner:
        query = query.join(User, Document.owner_id == User.id).where(
            or_(
                User.name.ilike(f"%{owner}%"),
                User.email.ilike(f"%{owner}%")
            )
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar() or 0

    # Apply pagination
    offset = (page - 1) * size
    query = query.order_by(Document.updated_at.desc()).offset(offset).limit(size)

    result = await db.execute(query)
    documents = result.scalars().unique().all()

    items = [build_document_response(doc) for doc in documents]
    pages = (total + size - 1) // size

    return DocumentListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/reports/review-due", response_model=DocumentListResponse)
async def get_review_due_documents(
    days: int = Query(90, description="Documents due for review within N days"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get documents that are due for review within the specified number of days."""
    due_date = date.today() + timedelta(days=days)

    query = select(Document).where(
        Document.next_review_date <= due_date,
        Document.status.in_([DocumentStatus.EFFECTIVE, DocumentStatus.APPROVED])
    ).options(
        selectinload(Document.document_type),
        selectinload(Document.versions),
        selectinload(Document.product_links).selectinload(DocumentProductLink.product)
    ).order_by(Document.next_review_date)

    result = await db.execute(query)
    documents = result.scalars().all()

    items = [build_document_response(doc) for doc in documents]

    return DocumentListResponse(
        items=items,
        total=len(items),
        page=1,
        size=len(items),
        pages=1
    )


@router.get("/reports/in-review", response_model=DocumentListResponse)
async def get_documents_in_review(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all documents currently in review."""
    query = select(Document).where(
        Document.status == DocumentStatus.IN_REVIEW
    ).options(
        selectinload(Document.document_type),
        selectinload(Document.versions),
        selectinload(Document.product_links).selectinload(DocumentProductLink.product)
    ).order_by(Document.updated_at.desc())

    result = await db.execute(query)
    documents = result.scalars().all()

    items = [build_document_response(doc) for doc in documents]

    return DocumentListResponse(
        items=items,
        total=len(items),
        page=1,
        size=len(items),
        pages=1
    )


@router.get("/reports/by-product/{product_id}", response_model=DocumentListResponse)
async def get_documents_by_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all documents linked to a specific product."""
    # Verify product exists
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    query = select(Document).join(DocumentProductLink).where(
        DocumentProductLink.product_id == product_id
    ).options(
        selectinload(Document.document_type),
        selectinload(Document.versions),
        selectinload(Document.product_links).selectinload(DocumentProductLink.product)
    ).order_by(Document.document_id)

    result = await db.execute(query)
    documents = result.scalars().unique().all()

    items = [build_document_response(doc) for doc in documents]

    return DocumentListResponse(
        items=items,
        total=len(items),
        page=1,
        size=len(items),
        pages=1
    )
