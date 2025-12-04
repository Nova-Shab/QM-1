"""
Template API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.template import Template
from app.models.user import User
from app.schemas.template import TemplateCreate, TemplateUpdate, TemplateResponse
from app.api.deps import get_current_user, get_admin_user
from app.services.audit import create_audit_log

router = APIRouter(prefix="/templates", tags=["Templates"])


@router.get("/", response_model=List[TemplateResponse])
async def list_templates(
    document_type_id: Optional[int] = None,
    language: Optional[str] = None,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all templates with optional filtering."""
    query = select(Template)

    if document_type_id:
        query = query.where(Template.document_type_id == document_type_id)

    if language:
        query = query.where(Template.language == language)

    if active_only:
        query = query.where(Template.is_active == True)

    query = query.order_by(Template.name)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific template by ID."""
    result = await db.execute(select(Template).where(Template.id == template_id))
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return template


@router.post("/", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: TemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Create a new template (admin only)."""
    template = Template(**template_data.model_dump())
    db.add(template)
    await db.commit()
    await db.refresh(template)

    await create_audit_log(
        db=db,
        entity_type="Template",
        entity_id=template.id,
        action="create",
        performed_by_id=current_user.id,
        details={"name": template.name}
    )

    return template


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    template_data: TemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update a template (admin only)."""
    result = await db.execute(select(Template).where(Template.id == template_id))
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    update_data = template_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)

    await db.commit()
    await db.refresh(template)

    await create_audit_log(
        db=db,
        entity_type="Template",
        entity_id=template.id,
        action="update",
        performed_by_id=current_user.id,
        details={"updated_fields": list(update_data.keys())}
    )

    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Deactivate a template (soft delete, admin only)."""
    result = await db.execute(select(Template).where(Template.id == template_id))
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    template.is_active = False
    await db.commit()

    await create_audit_log(
        db=db,
        entity_type="Template",
        entity_id=template.id,
        action="deactivate",
        performed_by_id=current_user.id,
        details={"soft_delete": True}
    )
