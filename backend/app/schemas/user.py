"""
User schemas for API validation.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    name: str
    role: UserRole = UserRole.READ_ONLY
    department: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    name: Optional[str] = None
    role: Optional[UserRole] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenPayload(BaseModel):
    """Schema for JWT token payload."""
    sub: str
    exp: datetime
