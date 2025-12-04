"""
API dependencies for authentication and authorization.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """Get the current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


def require_roles(*allowed_roles: UserRole):
    """
    Dependency factory for role-based access control.

    Usage:
        @router.post("/", dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.QA_APPROVER))])
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {[r.value for r in allowed_roles]}"
            )
        return current_user
    return role_checker


# Convenience dependencies for common role combinations
async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def get_author_or_above(current_user: User = Depends(get_current_user)) -> User:
    """Require at least author role (can create/edit documents)."""
    allowed = [UserRole.ADMIN, UserRole.AUTHOR, UserRole.QA_REVIEWER, UserRole.QA_APPROVER, UserRole.QP, UserRole.RA, UserRole.PRODUCTION]
    if current_user.role not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Author or higher role required"
        )
    return current_user


async def get_reviewer_or_above(current_user: User = Depends(get_current_user)) -> User:
    """Require at least reviewer role."""
    allowed = [UserRole.ADMIN, UserRole.QA_REVIEWER, UserRole.QA_APPROVER, UserRole.QP]
    if current_user.role not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Reviewer or higher role required"
        )
    return current_user


async def get_approver_or_above(current_user: User = Depends(get_current_user)) -> User:
    """Require at least approver role."""
    allowed = [UserRole.ADMIN, UserRole.QA_APPROVER, UserRole.QP]
    if current_user.role not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Approver or higher role required"
        )
    return current_user
