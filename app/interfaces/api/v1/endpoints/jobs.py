"""
Job API endpoints.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.application.schemas.job import (
    JobCreate, JobResponse, JobUpdate, JobListResponse, JobFilter, BaseResponse, PaginatedResponse
)
from app.application.services.job_service import JobService
from app.infrastructure.database.base import get_db
from app.infrastructure.repositories.job_repository import JobRepository
from app.infrastructure.repositories.user_repository import UserRepository
from app.core.exceptions import ValidationError, ConflictError, NotFoundError, AuthorizationError
from app.core.security import verify_token
from app.domain.entities.user import UserRole

router = APIRouter()


def get_job_service(db: Session = Depends(get_db)) -> JobService:
    """Get job service dependency."""
    job_repository = JobRepository(db)
    user_repository = UserRepository(db)
    return JobService(job_repository, user_repository)


security_scheme = HTTPBearer(scheme_name="Bearer Token", bearerFormat="JWT", auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(security_scheme),
) -> dict:
    """Get current user from JWT token (HTTP Bearer)."""
    if credentials is None or not credentials.scheme.lower() == "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return payload


@router.post("/", response_model=BaseResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_in: JobCreate,
    current_user: dict = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service)
) -> BaseResponse:
    """
    Create a new job (Company only).
    """
    try:
        user_id = UUID(current_user["sub"])
        if current_user.get("role") != UserRole.COMPANY.value:
            return BaseResponse(
                success=False,
                message="Only companies can create jobs",
                object=None,
                errors=["Company role required"]
            )
        job = await job_service.create(job_in, user_id)
        
        return BaseResponse(
            success=True,
            message="Job created successfully",
            object=JobResponse(
                id=job.id,
                title=job.title,
                description=job.description,
                location=job.location,
                status=job.status,
                created_by=job.created_by,
                created_at=job.created_at,
                updated_at=job.updated_at
            ).dict(),
            errors=None
        )
    except (ValidationError, ConflictError, NotFoundError, AuthorizationError) as e:
        return BaseResponse(
            success=False,
            message=str(e),
            object=None,
            errors=[str(e)]
        )


@router.get("/", response_model=PaginatedResponse)
async def get_jobs(
    title: Optional[str] = Query(None, description="Job title filter"),
    location: Optional[str] = Query(None, description="Job location filter"),
    company_name: Optional[str] = Query(None, description="Company name filter"),
    status: Optional[str] = Query(None, description="Job status filter"),
    page_number: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    current_user: dict = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service)
) -> PaginatedResponse:
    """
    Get all jobs with optional filters (Authenticated users).
    """
    try:
        filters = JobFilter(
            title=title,
            location=location,
            company_name=company_name,
            status=status,
            page_number=page_number,
            page_size=page_size
        )
        
        jobs = await job_service.search_jobs(filters)
        
        return PaginatedResponse(
            success=True,
            message="Jobs retrieved successfully",
            object=[JobResponse(
                id=job.id,
                title=job.title,
                description=job.description,
                location=job.location,
                status=job.status,
                created_by=job.created_by,
                created_at=job.created_at,
                updated_at=job.updated_at
            ).dict() for job in jobs],
            page_number=page_number,
            page_size=page_size,
            total_size=len(jobs),
            errors=None
        )
    except Exception as e:
        return PaginatedResponse(
            success=False,
            message="Error retrieving jobs",
            object=[],
            page_number=page_number,
            page_size=page_size,
            total_size=0,
            errors=[str(e)]
        )


@router.get("/{job_id}", response_model=BaseResponse)
async def get_job(
    job_id: UUID,
    current_user: dict = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service)
) -> BaseResponse:
    """
    Get job by ID (Authenticated users).
    """
    try:
        job = await job_service.get_by_id(job_id)
        if not job:
            return BaseResponse(
                success=False,
                message="Job not found",
                object=None,
                errors=["Job not found"]
            )
        
        return BaseResponse(
            success=True,
            message="Job retrieved successfully",
            object=JobResponse(
                id=job.id,
                title=job.title,
                description=job.description,
                location=job.location,
                status=job.status,
                created_by=job.created_by,
                created_at=job.created_at,
                updated_at=job.updated_at
            ).dict(),
            errors=None
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message="Error retrieving job",
            object=None,
            errors=[str(e)]
        )


@router.put("/{job_id}", response_model=BaseResponse)
async def update_job(
    job_id: UUID,
    job_in: JobUpdate,
    current_user: dict = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service)
) -> BaseResponse:
    """
    Update job (Company only, owner only).
    """
    try:
        user_id = UUID(current_user["sub"])
        job = await job_service.update(job_id, job_in, user_id)
        
        if not job:
            return BaseResponse(
                success=False,
                message="Job not found or unauthorized access",
                object=None,
                errors=["Job not found or unauthorized access"]
            )
        
        return BaseResponse(
            success=True,
            message="Job updated successfully",
            object=JobResponse(
                id=job.id,
                title=job.title,
                description=job.description,
                location=job.location,
                status=job.status,
                created_by=job.created_by,
                created_at=job.created_at,
                updated_at=job.updated_at
            ).dict(),
            errors=None
        )
    except (ValidationError, ConflictError, NotFoundError, AuthorizationError) as e:
        return BaseResponse(
            success=False,
            message=str(e),
            object=None,
            errors=[str(e)]
        )


@router.delete("/{job_id}", response_model=BaseResponse)
async def delete_job(
    job_id: UUID,
    current_user: dict = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service)
) -> BaseResponse:
    """
    Delete job (Company only, owner only).
    """
    try:
        user_id = UUID(current_user["sub"])
        deleted = await job_service.delete(job_id, user_id)
        
        if not deleted:
            return BaseResponse(
                success=False,
                message="Job not found or unauthorized access",
                object=None,
                errors=["Job not found or unauthorized access"]
            )
        
        return BaseResponse(
            success=True,
            message="Job deleted successfully",
            object=None,
            errors=None
        )
    except (ValidationError, ConflictError, NotFoundError, AuthorizationError) as e:
        return BaseResponse(
            success=False,
            message=str(e),
            object=None,
            errors=[str(e)]
        )


@router.get("/my-jobs", response_model=PaginatedResponse)
async def get_my_jobs(
    page_number: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    status: Optional[str] = Query(None, description="Job status filter"),
    current_user: dict = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service)
) -> PaginatedResponse:
    """
    Get jobs created by the current user (Company only).
    """
    try:
        user_id = UUID(current_user["sub"])
        # Enforce company role
        if current_user.get("role") != UserRole.COMPANY.value:
            return PaginatedResponse(
                success=False,
                message="Unauthorized access",
                object=[],
                page_number=page_number,
                page_size=page_size,
                total_size=0,
                errors=["Company role required"]
            )
        jobs = await job_service.get_by_creator(user_id, skip=(page_number - 1) * page_size, limit=page_size)
        
        return PaginatedResponse(
            success=True,
            message="Jobs retrieved successfully",
            object=[JobResponse(
                id=job.id,
                title=job.title,
                description=job.description,
                location=job.location,
                status=job.status,
                created_by=job.created_by,
                created_at=job.created_at,
                updated_at=job.updated_at
            ).dict() for job in jobs],
            page_number=page_number,
            page_size=page_size,
            total_size=len(jobs),
            errors=None
        )
    except Exception as e:
        return PaginatedResponse(
            success=False,
            message="Error retrieving jobs",
            object=[],
            page_number=page_number,
            page_size=page_size,
            total_size=0,
            errors=[str(e)]
        ) 