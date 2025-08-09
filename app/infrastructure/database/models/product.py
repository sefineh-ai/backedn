"""
Product database model.
"""
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Numeric
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
import uuid

from app.infrastructure.database.base import Base


class ProductModel(Base):
    """
    Product database model.
    
    This class represents the product table in the database,
    following SQLAlchemy ORM patterns.
    """
    
    __tablename__ = "products"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()), index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(String(1000), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    stock_quantity = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        return f"<ProductModel(id={self.id}, name={self.name}, sku={self.sku})>" 