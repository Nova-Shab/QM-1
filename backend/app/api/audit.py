"""
Audit log API endpoints.
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit_log import AuditLogResponse, AuditLogListResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/audit", tags=["Audit Trail"])


@router.get("/", response_model=AuditLogListResponse)
async def list_audit_logs(
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    action: Optional[str] = None,
    performed_by_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List audit log entries with filtering.

    The audit log is append-only and cannot be modified or deleted.
    """
    query = select(AuditLog).options(selectinload(AuditLog.performed_by_user))

    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)

    if entity_id:
        query = query.where(AuditLog.entity_id == entity_id)

    if action:
        query = query.where(AuditLog.action == action)

    if performed_by_id:
        query = query.where(AuditLog.performed_by_id == performed_by_id)

    if start_date:
        query = query.where(AuditLog.timestamp >= start_date)

    if end_date:
        query = query.where(AuditLog.timestamp <= end_date)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar() or 0

    # Apply pagination (newest first)
    offset = (page - 1) * size
    query = query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(size)

    result = await db.execute(query)
    logs = result.scalars().all()

    items = []
    for log in logs:
        items.append(AuditLogResponse(
            id=log.id,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            action=log.action,
            performed_by_id=log.performed_by_id,
            performed_by_name=log.performed_by_user.name if log.performed_by_user else None,
            timestamp=log.timestamp,
            details=log.details,
            description=log.description,
            ip_address=log.ip_address
        ))

    pages = (total + size - 1) // size

    return AuditLogListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/entity/{entity_type}/{entity_id}", response_model=List[AuditLogResponse])
async def get_entity_audit_trail(
    entity_type: str,
    entity_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get complete audit trail for a specific entity."""
    query = select(AuditLog).where(
        AuditLog.entity_type == entity_type,
        AuditLog.entity_id == entity_id
    ).options(
        selectinload(AuditLog.performed_by_user)
    ).order_by(AuditLog.timestamp.desc())

    result = await db.execute(query)
    logs = result.scalars().all()

    items = []
    for log in logs:
        items.append(AuditLogResponse(
            id=log.id,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            action=log.action,
            performed_by_id=log.performed_by_id,
            performed_by_name=log.performed_by_user.name if log.performed_by_user else None,
            timestamp=log.timestamp,
            details=log.details,
            description=log.description,
            ip_address=log.ip_address
        ))

    return items
