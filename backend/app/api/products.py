"""
Product API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.core.database import get_db
from app.models.product import Product, MarketStatus
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.api.deps import get_current_user, get_author_or_above
from app.services.audit import create_audit_log

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=List[ProductResponse])
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = None,
    market_status: Optional[MarketStatus] = None,
    product_family: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all products with optional filtering."""
    query = select(Product)

    if search:
        query = query.where(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.short_name.ilike(f"%{search}%")
            )
        )

    if market_status:
        query = query.where(Product.market_status == market_status)

    if product_family:
        query = query.where(Product.product_family == product_family)

    query = query.order_by(Product.name).offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific product by ID."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return product


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_author_or_above)
):
    """Create a new product."""
    product = Product(**product_data.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)

    # Create audit log
    await create_audit_log(
        db=db,
        entity_type="Product",
        entity_id=product.id,
        action="create",
        performed_by_id=current_user.id,
        details={"name": product.name}
    )

    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_author_or_above)
):
    """Update a product."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)

    # Create audit log
    await create_audit_log(
        db=db,
        entity_type="Product",
        entity_id=product.id,
        action="update",
        performed_by_id=current_user.id,
        details={"updated_fields": list(update_data.keys())}
    )

    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_author_or_above)
):
    """Delete a product (soft delete by setting market_status to discontinued)."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Soft delete - just mark as discontinued
    product.market_status = MarketStatus.DISCONTINUED
    await db.commit()

    # Create audit log
    await create_audit_log(
        db=db,
        entity_type="Product",
        entity_id=product.id,
        action="delete",
        performed_by_id=current_user.id,
        details={"soft_delete": True}
    )
