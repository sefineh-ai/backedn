"""
Product schemas for API requests and responses.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    """Base product schema."""
    
    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    description: str = Field(..., min_length=1, max_length=1000, description="Product description")
    price: Decimal = Field(..., ge=0, description="Product price")
    sku: str = Field(..., min_length=1, max_length=50, description="Stock keeping unit")
    category: str = Field(..., min_length=1, max_length=100, description="Product category")
    stock_quantity: int = Field(default=0, ge=0, description="Available stock quantity")


class ProductCreate(ProductBase):
    """Schema for creating a product."""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Product name")
    description: Optional[str] = Field(None, min_length=1, max_length=1000, description="Product description")
    price: Optional[Decimal] = Field(None, ge=0, description="Product price")
    sku: Optional[str] = Field(None, min_length=1, max_length=50, description="Stock keeping unit")
    category: Optional[str] = Field(None, min_length=1, max_length=100, description="Product category")
    stock_quantity: Optional[int] = Field(None, ge=0, description="Available stock quantity")
    is_active: Optional[bool] = Field(None, description="Product active status")


class ProductResponse(ProductBase):
    """Schema for product response."""
    
    id: UUID = Field(description="Product unique identifier")
    is_active: bool = Field(description="Product active status")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
            Decimal: lambda v: float(v)
        }


class ProductListResponse(BaseModel):
    """Schema for product list response."""
    
    products: list[ProductResponse] = Field(description="List of products")
    total: int = Field(description="Total number of products")
    skip: int = Field(description="Number of records skipped")
    limit: int = Field(description="Maximum number of records returned")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
            Decimal: lambda v: float(v)
        } 