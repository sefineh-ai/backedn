"""
Application API endpoints.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.application.schemas.application import (
    ApplicationCreate, ApplicationResponse, ApplicationUpdate, ApplicationListResponse, 
    ApplicationFilter, BaseResponse, PaginatedResponse
)
from app.application.services.application_service import ApplicationService
from app.infrastructure.database.base import get_db
from app.infrastructure.repositories.application_repository import ApplicationRepository
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.job_repository import JobRepository
from app.core.exceptions import ValidationError, ConflictError, NotFoundError, AuthorizationError
from app.core.security import verify_token
from app.domain.entities.user import UserRole

router = APIRouter()


def get_application_service(db: Session = Depends(get_db)) -> ApplicationService:
    """Get application service dependency."""
    application_repository = ApplicationRepository(db)
    user_repository = UserRepository(db)
    job_repository = JobRepository(db)
    return ApplicationService(application_repository, user_repository, job_repository)


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
async def create_application(
    application_in: ApplicationCreate,
    current_user: dict = Depends(get_current_user),
    application_service: ApplicationService = Depends(get_application_service)
) -> BaseResponse:
    """
    Create a new application (Applicant only).
    """
    try:
        applicant_id = UUID(current_user["sub"])
        if current_user.get("role") != UserRole.APPLICANT.value:
            return BaseResponse(success=False, message="Only applicants can apply", object=None, errors=["Applicant role required"])
        application = await application_service.create(application_in, applicant_id)
        
        return BaseResponse(
            success=True,
            message="Application submitted successfully",
            object=ApplicationResponse(
                id=application.id,
                applicant_id=application.applicant_id,
                job_id=application.job_id,
                resume_link=application.resume_link,
                cover_letter=application.cover_letter,
                status=application.status,
                applied_at=application.applied_at,
                updated_at=application.updated_at
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


@router.get("/my-applications", response_model=PaginatedResponse)
async def get_my_applications(
    page_number: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    company_name: Optional[str] = Query(None, description="Company name filter"),
    job_status: Optional[str] = Query(None, description="Job status filter"),
    application_status: Optional[List[str]] = Query(None, description="Application status filter"),
    sort_by: Optional[str] = Query("applied_at", description="Sort by field"),
    sort_order: Optional[str] = Query("desc", description="Sort order"),
    current_user: dict = Depends(get_current_user),
    application_service: ApplicationService = Depends(get_application_service)
) -> PaginatedResponse:
    """
    Get applications submitted by the current user (Applicant only).
    """
    try:
        applicant_id = UUID(current_user["sub"])
        if current_user.get("role") != UserRole.APPLICANT.value:
            return PaginatedResponse(success=False, message="Unauthorized access", object=[], page_number=page_number, page_size=page_size, total_size=0, errors=["Applicant role required"])
        filters = ApplicationFilter(
            company_name=company_name,
            job_status=job_status,
            application_status=application_status,
            sort_by=sort_by,
            sort_order=sort_order,
            page_number=page_number,
            page_size=page_size
        )
        
        applications = await application_service.search_applications(filters, applicant_id)
        
        return PaginatedResponse(
            success=True,
            message="Applications retrieved successfully",
            object=[ApplicationResponse(
                id=app.id,
                applicant_id=app.applicant_id,
                job_id=app.job_id,
                resume_link=app.resume_link,
                cover_letter=app.cover_letter,
                status=app.status,
                applied_at=app.applied_at,
                updated_at=app.updated_at
            ).dict() for app in applications],
            page_number=page_number,
            page_size=page_size,
            total_size=len(applications),
            errors=None
        )
    except Exception as e:
        return PaginatedResponse(
            success=False,
            message="Error retrieving applications",
            object=[],
            page_number=page_number,
            page_size=page_size,
            total_size=0,
            errors=[str(e)]
        )


@router.get("/job/{job_id}", response_model=PaginatedResponse)
async def get_job_applications(
    job_id: UUID,
    page_number: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    status: Optional[str] = Query(None, description="Application status filter"),
    current_user: dict = Depends(get_current_user),
    application_service: ApplicationService = Depends(get_application_service)
) -> PaginatedResponse:
    """
    Get applications for a specific job (Company only, owner only).
    """
    try:
        user_id = UUID(current_user["sub"])
        if current_user.get("role") != UserRole.COMPANY.value:
            return PaginatedResponse(success=False, message="Unauthorized access", object=[], page_number=page_number, page_size=page_size, total_size=0, errors=["Company role required"])
        applications = await application_service.get_by_job(job_id, user_id, skip=(page_number - 1) * page_size, limit=page_size)
        
        return PaginatedResponse(
            success=True,
            message="Applications retrieved successfully",
            object=[ApplicationResponse(
                id=app.id,
                applicant_id=app.applicant_id,
                job_id=app.job_id,
                resume_link=app.resume_link,
                cover_letter=app.cover_letter,
                status=app.status,
                applied_at=app.applied_at,
                updated_at=app.updated_at
            ).dict() for app in applications],
            page_number=page_number,
            page_size=page_size,
            total_size=len(applications),
            errors=None
        )
    except (ValidationError, ConflictError, NotFoundError, AuthorizationError) as e:
        return PaginatedResponse(
            success=False,
            message=str(e),
            object=[],
            page_number=page_number,
            page_size=page_size,
            total_size=0,
            errors=[str(e)]
        )


@router.put("/{application_id}/status", response_model=BaseResponse)
async def update_application_status(
    application_id: UUID,
    application_in: ApplicationUpdate,
    current_user: dict = Depends(get_current_user),
    application_service: ApplicationService = Depends(get_application_service)
) -> BaseResponse:
    """
    Update application status (Company only, job owner only).
    """
    try:
        user_id = UUID(current_user["sub"])
        if current_user.get("role") != UserRole.COMPANY.value:
            return BaseResponse(success=False, message="Unauthorized", object=None, errors=["Company role required"])
        application = await application_service.update_status(application_id, application_in, user_id)
        
        if not application:
            return BaseResponse(
                success=False,
                message="Application not found or unauthorized access",
                object=None,
                errors=["Application not found or unauthorized access"]
            )
        
        return BaseResponse(
            success=True,
            message="Application status updated successfully",
            object=ApplicationResponse(
                id=application.id,
                applicant_id=application.applicant_id,
                job_id=application.job_id,
                resume_link=application.resume_link,
                cover_letter=application.cover_letter,
                status=application.status,
                applied_at=application.applied_at,
                updated_at=application.updated_at
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


@router.get("/{application_id}", response_model=BaseResponse)
async def get_application(
    application_id: UUID,
    current_user: dict = Depends(get_current_user),
    application_service: ApplicationService = Depends(get_application_service)
) -> BaseResponse:
    """
    Get application by ID.
    """
    try:
        application = await application_service.get_by_id(application_id)
        if not application:
            return BaseResponse(
                success=False,
                message="Application not found",
                object=None,
                errors=["Application not found"]
            )
        
        return BaseResponse(
            success=True,
            message="Application retrieved successfully",
            object=ApplicationResponse(
                id=application.id,
                applicant_id=application.applicant_id,
                job_id=application.job_id,
                resume_link=application.resume_link,
                cover_letter=application.cover_letter,
                status=application.status,
                applied_at=application.applied_at,
                updated_at=application.updated_at
            ).dict(),
            errors=None
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message="Error retrieving application",
            object=None,
            errors=[str(e)]
        ) 