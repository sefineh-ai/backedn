"""
Products API endpoints.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.application.schemas.product import ProductCreate, ProductResponse, ProductUpdate, ProductListResponse
from app.application.services.product_service import ProductService
from app.infrastructure.database.base import get_db
from app.infrastructure.repositories.product_repository import ProductRepository

router = APIRouter()


def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    """
    Dependency to get product service.
    
    Args:
        db: Database session
        
    Returns:
        ProductService instance
    """
    product_repository = ProductRepository(db)
    return ProductService(product_repository)


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate,
    product_service: ProductService = Depends(get_product_service)
) -> ProductResponse:
    """
    Create a new product.
    
    Args:
        product_in: Product creation data
        product_service: Product service
        
    Returns:
        Created product
        
    Raises:
        HTTPException: If product creation fails
    """
    try:
        product = await product_service.create(product_in)
        return ProductResponse(**product.dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    product_service: ProductService = Depends(get_product_service)
) -> ProductResponse:
    """
    Get product by ID.
    
    Args:
        product_id: Product ID
        product_service: Product service
        
    Returns:
        Product data
        
    Raises:
        HTTPException: If product not found
    """
    product = await product_service.get_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return ProductResponse(**product.dict())


@router.get("/", response_model=ProductListResponse)
async def get_products(
    skip: int = 0,
    limit: int = 100,
    product_service: ProductService = Depends(get_product_service)
) -> ProductListResponse:
    """
    Get all products with pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        product_service: Product service
        
    Returns:
        List of products with pagination info
    """
    products = await product_service.get_all(skip=skip, limit=limit)
    return ProductListResponse(
        products=[ProductResponse(**product.dict()) for product in products],
        total=len(products),
        skip=skip,
        limit=limit
    )


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    product_in: ProductUpdate,
    product_service: ProductService = Depends(get_product_service)
) -> ProductResponse:
    """
    Update product.
    
    Args:
        product_id: Product ID
        product_in: Product update data
        product_service: Product service
        
    Returns:
        Updated product data
        
    Raises:
        HTTPException: If product not found or update fails
    """
    try:
        product = await product_service.update(product_id, product_in)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return ProductResponse(**product.dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: UUID,
    product_service: ProductService = Depends(get_product_service)
) -> None:
    """
    Delete product.
    
    Args:
        product_id: Product ID
        product_service: Product service
        
    Raises:
        HTTPException: If product not found or deletion fails
    """
    try:
        deleted = await product_service.delete(product_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{product_id}/stock", response_model=ProductResponse)
async def update_product_stock(
    product_id: UUID,
    quantity: int,
    product_service: ProductService = Depends(get_product_service)
) -> ProductResponse:
    """
    Update product stock.
    
    Args:
        product_id: Product ID
        quantity: New stock quantity
        product_service: Product service
        
    Returns:
        Updated product data
        
    Raises:
        HTTPException: If product not found or update fails
    """
    try:
        product = await product_service.update_stock(product_id, quantity)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return ProductResponse(**product.dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 