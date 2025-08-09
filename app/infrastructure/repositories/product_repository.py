"""
Product repository implementation.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.interfaces import RepositoryInterface
from app.domain.entities.product import Product
from app.infrastructure.database.models.product import ProductModel


class ProductRepository(RepositoryInterface[Product]):
    """
    Product repository implementation.
    
    This class implements the Repository pattern for product data access,
    following the Dependency Inversion Principle.
    """
    
    def __init__(self, db: Session):
        """
        Initialize ProductRepository with database session.
        
        Args:
            db: Database session
        """
        self.db = db
    
    async def create(self, obj_in: Product) -> Product:
        """
        Create a new product.
        
        Args:
            obj_in: Product entity to create
            
        Returns:
            Created product entity
        """
        db_obj = ProductModel(
            id=str(obj_in.id),
            name=obj_in.name,
            description=obj_in.description,
            price=obj_in.price,
            sku=obj_in.sku,
            category=obj_in.category,
            stock_quantity=obj_in.stock_quantity,
            is_active=obj_in.is_active,
            created_at=obj_in.created_at,
            updated_at=obj_in.updated_at
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return self._to_entity(db_obj)
    
    async def get_by_id(self, id: UUID) -> Optional[Product]:
        """
        Get product by ID.
        
        Args:
            id: Product ID
            
        Returns:
            Product entity if found, None otherwise
        """
        db_obj = self.db.query(ProductModel).filter(ProductModel.id == str(id)).first()
        return self._to_entity(db_obj) if db_obj else None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Get all products with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of product entities
        """
        db_objs = self.db.query(ProductModel).offset(skip).limit(limit).all()
        return [self._to_entity(db_obj) for db_obj in db_objs]
    
    async def update(self, id: UUID, obj_in: Product) -> Optional[Product]:
        """
        Update product.
        
        Args:
            id: Product ID
            obj_in: Product entity with updated data
            
        Returns:
            Updated product entity if found, None otherwise
        """
        db_obj = self.db.query(ProductModel).filter(ProductModel.id == str(id)).first()
        if not db_obj:
            return None
        
        # Update fields
        for field, value in obj_in.dict(exclude={'id'}).items():
            setattr(db_obj, field, value)
        
        self.db.commit()
        self.db.refresh(db_obj)
        return self._to_entity(db_obj)
    
    async def delete(self, id: UUID) -> bool:
        """
        Delete product.
        
        Args:
            id: Product ID
            
        Returns:
            True if deleted successfully, False otherwise
        """
        db_obj = self.db.query(ProductModel).filter(ProductModel.id == str(id)).first()
        if not db_obj:
            return False
        
        self.db.delete(db_obj)
        self.db.commit()
        return True
    
    async def exists(self, id: UUID) -> bool:
        """
        Check if product exists.
        
        Args:
            id: Product ID
            
        Returns:
            True if product exists, False otherwise
        """
        return self.db.query(ProductModel).filter(ProductModel.id == str(id)).first() is not None
    
    async def get_by_sku(self, sku: str) -> Optional[Product]:
        """
        Get product by SKU.
        
        Args:
            sku: Product SKU
            
        Returns:
            Product entity if found, None otherwise
        """
        db_obj = self.db.query(ProductModel).filter(ProductModel.sku == sku).first()
        return self._to_entity(db_obj) if db_obj else None
    
    async def get_by_category(self, category: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Get products by category.
        
        Args:
            category: Product category
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of product entities
        """
        db_objs = self.db.query(ProductModel).filter(
            ProductModel.category == category
        ).offset(skip).limit(limit).all()
        return [self._to_entity(db_obj) for db_obj in db_objs]
    
    def _to_entity(self, db_obj: ProductModel) -> Product:
        """
        Convert database model to domain entity.
        
        Args:
            db_obj: Database model
            
        Returns:
            Domain entity
        """
        return Product(
            id=UUID(db_obj.id),
            name=db_obj.name,
            description=db_obj.description,
            price=db_obj.price,
            sku=db_obj.sku,
            category=db_obj.category,
            stock_quantity=db_obj.stock_quantity,
            is_active=db_obj.is_active,
            created_at=db_obj.created_at,
            updated_at=db_obj.updated_at
        ) 