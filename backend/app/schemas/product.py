"""
Product schemas for API validation.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.models.product import DosageForm, MarketStatus


class ProductBase(BaseModel):
    """Base product schema."""
    name: str
    short_name: str
    dosage_form: DosageForm
    strength: Optional[str] = None
    product_family: Optional[str] = None
    market_status: MarketStatus = MarketStatus.IN_DEVELOPMENT
    country: str = "DE"
    description: Optional[str] = None
    ma_number: Optional[str] = None


class ProductCreate(ProductBase):
    """Schema for creating a new product."""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product."""
    name: Optional[str] = None
    short_name: Optional[str] = None
    dosage_form: Optional[DosageForm] = None
    strength: Optional[str] = None
    product_family: Optional[str] = None
    market_status: Optional[MarketStatus] = None
    country: Optional[str] = None
    description: Optional[str] = None
    ma_number: Optional[str] = None


class ProductResponse(ProductBase):
    """Schema for product response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
