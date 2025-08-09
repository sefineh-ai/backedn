"""
Main FastAPI application.
"""
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.exceptions import BaseException
from app.infrastructure.database.base import DatabaseManager, get_db
from app.interfaces.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    This function handles application startup and shutdown events.
    """
    # Startup
    print("Starting up...")
    db_manager = DatabaseManager()
    db_manager.create_tables()
    print("Database tables created.")
    
    yield
    
    # Shutdown
    print("Shutting down...")


def create_application() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Job Board API - Enterprise-level backend using Design Patterns, SOLID principles, and OOP",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan
    )
    
    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"] if settings.debug else ["localhost", "127.0.0.1"]
    )
    
    # Include routers
    app.include_router(api_router, prefix="/api/v1")
    
    # Exception handlers
    @app.exception_handler(BaseException)
    async def custom_exception_handler(request: Request, exc: BaseException) -> JSONResponse:
        """Handle custom exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.message,
                "object": None,
                "errors": [exc.details] if exc.details else None
            }
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        """Handle HTTP exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.detail,
                "object": None,
                "errors": None
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Handle validation exceptions."""
        errors = []
        for error in exc.errors():
            errors.append(f"{error['loc'][-1]}: {error['msg']}")
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "message": "Validation error",
                "object": None,
                "errors": errors
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle general exceptions."""
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Internal server error",
                "object": None,
                "errors": [str(exc)] if settings.debug else None
            }
        )
    
    return app


# Create application instance
app = create_application()


@app.get("/")
async def root() -> dict[str, Any]:
    """
    Root endpoint.
    
    Returns:
        Welcome message and API information
    """
    return {
        "success": True,
        "message": "Welcome to Job Board API",
        "object": {
            "name": settings.app_name,
            "version": settings.app_version,
            "description": "Enterprise-level job board backend using Design Patterns, SOLID principles, and OOP",
            "docs_url": "/docs",
            "health_check": "/health"
        },
        "errors": None
    }


@app.get("/health")
async def health_check() -> dict[str, Any]:
    """
    Health check endpoint.
    
    Returns:
        Health status information
    """
    return {
        "success": True,
        "message": "Service is healthy",
        "object": {
            "status": "healthy",
            "service": settings.app_name,
            "version": settings.app_version
        },
        "errors": None
    } 