"""
Product domain entity.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class Product(BaseModel):
    """
    Product domain entity.
    
    This class represents a product in the domain layer,
    following the Domain-Driven Design principles.
    """
    
    id: UUID = Field(default_factory=uuid4, description="Product unique identifier")
    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    description: str = Field(..., min_length=1, max_length=1000, description="Product description")
    price: Decimal = Field(..., ge=0, description="Product price")
    sku: str = Field(..., min_length=1, max_length=50, description="Stock keeping unit")
    category: str = Field(..., min_length=1, max_length=100, description="Product category")
    stock_quantity: int = Field(default=0, ge=0, description="Available stock quantity")
    is_active: bool = Field(default=True, description="Product active status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    @validator('name')
    def validate_name(cls, v: str) -> str:
        """Validate product name."""
        if len(v.strip()) < 1:
            raise ValueError('Product name cannot be empty')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v: str) -> str:
        """Validate product description."""
        if len(v.strip()) < 1:
            raise ValueError('Product description cannot be empty')
        return v.strip()
    
    @validator('sku')
    def validate_sku(cls, v: str) -> str:
        """Validate SKU format."""
        if not v.isalnum():
            raise ValueError('SKU must contain only alphanumeric characters')
        return v.upper()
    
    @validator('price')
    def validate_price(cls, v: Decimal) -> Decimal:
        """Validate price."""
        if v < 0:
            raise ValueError('Price cannot be negative')
        return v
    
    def update_stock(self, quantity: int) -> None:
        """Update stock quantity."""
        if quantity < 0:
            raise ValueError('Stock quantity cannot be negative')
        self.stock_quantity = quantity
        self.updated_at = datetime.utcnow()
    
    def add_stock(self, quantity: int) -> None:
        """Add stock quantity."""
        if quantity < 0:
            raise ValueError('Quantity to add cannot be negative')
        self.stock_quantity += quantity
        self.updated_at = datetime.utcnow()
    
    def remove_stock(self, quantity: int) -> None:
        """Remove stock quantity."""
        if quantity < 0:
            raise ValueError('Quantity to remove cannot be negative')
        if self.stock_quantity < quantity:
            raise ValueError('Insufficient stock')
        self.stock_quantity -= quantity
        self.updated_at = datetime.utcnow()
    
    def update_price(self, new_price: Decimal) -> None:
        """Update product price."""
        if new_price < 0:
            raise ValueError('Price cannot be negative')
        self.price = new_price
        self.updated_at = datetime.utcnow()
    
    def activate(self) -> None:
        """Activate the product."""
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        """Deactivate the product."""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def is_in_stock(self) -> bool:
        """Check if product is in stock."""
        return self.stock_quantity > 0
    
    def is_available(self) -> bool:
        """Check if product is available for purchase."""
        return self.is_active and self.is_in_stock()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
            Decimal: lambda v: float(v)
        } 