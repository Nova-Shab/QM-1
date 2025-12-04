"""
User management API endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.api.deps import get_current_user, get_admin_user
from app.services.audit import create_audit_log

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all users."""
    result = await db.execute(select(User).order_by(User.name))
    return result.scalars().all()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Create a new user (admin only)."""
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,
        department=user_data.department
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    await create_audit_log(
        db=db,
        entity_type="User",
        entity_id=user.id,
        action="create",
        performed_by_id=current_user.id,
        details={"email": user.email, "role": user.role.value}
    )

    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update a user (admin only)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)

    await create_audit_log(
        db=db,
        entity_type="User",
        entity_id=user.id,
        action="update",
        performed_by_id=current_user.id,
        details={"updated_fields": list(update_data.keys())}
    )

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Deactivate a user (soft delete, admin only)."""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot deactivate your own account"
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    await db.commit()

    await create_audit_log(
        db=db,
        entity_type="User",
        entity_id=user.id,
        action="deactivate",
        performed_by_id=current_user.id,
        details={"soft_delete": True}
    )
