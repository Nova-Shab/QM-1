"""
Document type API endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.document_type import DocumentType
from app.models.user import User
from app.schemas.document_type import DocumentTypeCreate, DocumentTypeUpdate, DocumentTypeResponse
from app.api.deps import get_current_user, get_admin_user
from app.services.audit import create_audit_log

router = APIRouter(prefix="/document-types", tags=["Document Types"])


@router.get("/", response_model=List[DocumentTypeResponse])
async def list_document_types(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all document types."""
    result = await db.execute(select(DocumentType).order_by(DocumentType.code))
    return result.scalars().all()


@router.get("/{document_type_id}", response_model=DocumentTypeResponse)
async def get_document_type(
    document_type_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific document type by ID."""
    result = await db.execute(select(DocumentType).where(DocumentType.id == document_type_id))
    doc_type = result.scalar_one_or_none()

    if not doc_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document type not found"
        )

    return doc_type


@router.post("/", response_model=DocumentTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_document_type(
    doc_type_data: DocumentTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Create a new document type (admin only)."""
    # Check if code already exists
    result = await db.execute(select(DocumentType).where(DocumentType.code == doc_type_data.code))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document type code already exists"
        )

    doc_type = DocumentType(**doc_type_data.model_dump())
    db.add(doc_type)
    await db.commit()
    await db.refresh(doc_type)

    await create_audit_log(
        db=db,
        entity_type="DocumentType",
        entity_id=doc_type.id,
        action="create",
        performed_by_id=current_user.id,
        details={"code": doc_type.code, "name": doc_type.name}
    )

    return doc_type


@router.put("/{document_type_id}", response_model=DocumentTypeResponse)
async def update_document_type(
    document_type_id: int,
    doc_type_data: DocumentTypeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update a document type (admin only)."""
    result = await db.execute(select(DocumentType).where(DocumentType.id == document_type_id))
    doc_type = result.scalar_one_or_none()

    if not doc_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document type not found"
        )

    update_data = doc_type_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(doc_type, field, value)

    await db.commit()
    await db.refresh(doc_type)

    await create_audit_log(
        db=db,
        entity_type="DocumentType",
        entity_id=doc_type.id,
        action="update",
        performed_by_id=current_user.id,
        details={"updated_fields": list(update_data.keys())}
    )

    return doc_type
