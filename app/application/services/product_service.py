"""
Product service implementation.
"""
from typing import List, Optional
from uuid import UUID

from app.core.interfaces import ServiceInterface
from app.domain.entities.product import Product
from app.application.schemas.product import ProductCreate, ProductUpdate


class ProductService(ServiceInterface[Product]):
    """
    Product service implementation.
    
    This service handles business logic for product operations,
    following the Single Responsibility Principle and
    implementing the Service pattern.
    """
    
    def __init__(self, product_repository, cache_service=None, event_publisher=None):
        """
        Initialize ProductService with dependencies.
        
        Args:
            product_repository: Repository for product data access
            cache_service: Cache service for performance optimization
            event_publisher: Event publisher for domain events
        """
        self._repository = product_repository
        self._cache = cache_service
        self._event_publisher = event_publisher
    
    async def create(self, obj_in: ProductCreate) -> Product:
        """
        Create a new product with business logic validation.
        
        Args:
            obj_in: Product creation data
            
        Returns:
            Created product entity
            
        Raises:
            ValidationError: If product data is invalid
            ConflictError: If product already exists
        """
        # Check if product already exists
        existing_product = await self._repository.get_by_sku(obj_in.sku)
        if existing_product:
            raise ConflictError(f"Product with SKU {obj_in.sku} already exists")
        
        # Create product entity
        product = Product(
            name=obj_in.name,
            description=obj_in.description,
            price=obj_in.price,
            sku=obj_in.sku,
            category=obj_in.category,
            stock_quantity=obj_in.stock_quantity
        )
        
        # Save to repository
        created_product = await self._repository.create(product)
        
        # Cache the product
        if self._cache:
            await self._cache.set(f"product:{created_product.id}", created_product.dict())
        
        # Publish product created event
        if self._event_publisher:
            await self._event_publisher.publish(
                "product.created",
                {"product_id": str(created_product.id), "sku": created_product.sku}
            )
        
        return created_product
    
    async def get_by_id(self, id: UUID) -> Optional[Product]:
        """
        Get product by ID with caching.
        
        Args:
            id: Product ID
            
        Returns:
            Product entity if found, None otherwise
        """
        # Try to get from cache first
        if self._cache:
            cached_product = await self._cache.get(f"product:{id}")
            if cached_product:
                return Product(**cached_product)
        
        # Get from repository
        product = await self._repository.get_by_id(id)
        
        # Cache the product if found
        if product and self._cache:
            await self._cache.set(f"product:{id}", product.dict())
        
        return product
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Get all products with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of product entities
        """
        return await self._repository.get_all(skip=skip, limit=limit)
    
    async def update(self, id: UUID, obj_in: ProductUpdate) -> Optional[Product]:
        """
        Update product with business logic validation.
        
        Args:
            id: Product ID
            obj_in: Product update data
            
        Returns:
            Updated product entity if found, None otherwise
            
        Raises:
            ValidationError: If update data is invalid
            NotFoundError: If product not found
        """
        # Get existing product
        product = await self.get_by_id(id)
        if not product:
            raise NotFoundError(f"Product with ID {id} not found")
        
        # Update product fields
        if obj_in.name is not None:
            product.name = obj_in.name
        
        if obj_in.description is not None:
            product.description = obj_in.description
        
        if obj_in.price is not None:
            product.update_price(obj_in.price)
        
        if obj_in.sku is not None:
            # Check if SKU is already taken by another product
            existing_product = await self._repository.get_by_sku(obj_in.sku)
            if existing_product and existing_product.id != id:
                raise ConflictError(f"SKU {obj_in.sku} is already taken")
            product.sku = obj_in.sku
        
        if obj_in.category is not None:
            product.category = obj_in.category
        
        if obj_in.stock_quantity is not None:
            product.update_stock(obj_in.stock_quantity)
        
        if obj_in.is_active is not None:
            if obj_in.is_active:
                product.activate()
            else:
                product.deactivate()
        
        # Save to repository
        updated_product = await self._repository.update(id, product)
        
        # Update cache
        if self._cache and updated_product:
            await self._cache.set(f"product:{id}", updated_product.dict())
        
        # Publish product updated event
        if self._event_publisher and updated_product:
            await self._event_publisher.publish(
                "product.updated",
                {"product_id": str(id), "sku": updated_product.sku}
            )
        
        return updated_product
    
    async def delete(self, id: UUID) -> bool:
        """
        Delete product with business logic.
        
        Args:
            id: Product ID
            
        Returns:
            True if deleted successfully, False otherwise
            
        Raises:
            NotFoundError: If product not found
        """
        # Check if product exists
        product = await self.get_by_id(id)
        if not product:
            raise NotFoundError(f"Product with ID {id} not found")
        
        # Delete from repository
        deleted = await self._repository.delete(id)
        
        # Remove from cache
        if self._cache and deleted:
            await self._cache.delete(f"product:{id}")
        
        # Publish product deleted event
        if self._event_publisher and deleted:
            await self._event_publisher.publish(
                "product.deleted",
                {"product_id": str(id), "sku": product.sku}
            )
        
        return deleted
    
    async def update_stock(self, id: UUID, quantity: int) -> Optional[Product]:
        """
        Update product stock.
        
        Args:
            id: Product ID
            quantity: New stock quantity
            
        Returns:
            Updated product entity if found, None otherwise
        """
        product = await self.get_by_id(id)
        if not product:
            raise NotFoundError(f"Product with ID {id} not found")
        
        product.update_stock(quantity)
        updated_product = await self._repository.update(id, product)
        
        # Update cache
        if self._cache and updated_product:
            await self._cache.set(f"product:{id}", updated_product.dict())
        
        return updated_product
    
    async def get_by_sku(self, sku: str) -> Optional[Product]:
        """
        Get product by SKU.
        
        Args:
            sku: Product SKU
            
        Returns:
            Product entity if found, None otherwise
        """
        return await self._repository.get_by_sku(sku)
    
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
        return await self._repository.get_by_category(category, skip=skip, limit=limit) 