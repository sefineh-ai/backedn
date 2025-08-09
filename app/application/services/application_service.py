"""
Application service implementation.
"""
from typing import List, Optional
from uuid import UUID

from app.core.interfaces import ServiceInterface
from app.core.exceptions import ValidationError, ConflictError, NotFoundError, AuthorizationError
from app.domain.entities.application import Application, ApplicationStatus
from app.domain.entities.user import UserRole
from app.application.schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationFilter
from app.infrastructure.repositories.application_repository import ApplicationRepository
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.job_repository import JobRepository


class ApplicationService(ServiceInterface[Application]):
    """
    Application service implementation.
    
    This class implements the Service pattern for application business logic,
    following the Clean Architecture principles.
    """
    
    def __init__(self, application_repository: ApplicationRepository, 
                 user_repository: UserRepository, job_repository: JobRepository):
        self.application_repository = application_repository
        self.user_repository = user_repository
        self.job_repository = job_repository
    
    async def create(self, obj_in: ApplicationCreate, applicant_id: UUID) -> Application:
        """Create a new application."""
        # Verify applicant is an applicant
        applicant = await self.user_repository.get_by_id(applicant_id)
        if not applicant:
            raise NotFoundError(f"User with ID {applicant_id} not found")
        
        if applicant.role != UserRole.APPLICANT:
            raise AuthorizationError("Only applicants can apply for jobs")
        
        # Verify job exists and is open
        job = await self.job_repository.get_by_id(obj_in.job_id)
        if not job:
            raise NotFoundError(f"Job with ID {obj_in.job_id} not found")
        
        if not job.is_open():
            raise ValidationError("Cannot apply to a job that is not open")
        
        # Check if applicant already applied to this job
        existing_application = await self.application_repository.get_by_applicant_and_job(
            applicant_id, obj_in.job_id
        )
        if existing_application:
            raise ConflictError("You have already applied to this job")
        
        # Create application entity
        application = Application(
            applicant_id=applicant_id,
            job_id=obj_in.job_id,
            resume_link=obj_in.resume_link,
            cover_letter=obj_in.cover_letter,
            status=ApplicationStatus.APPLIED
        )
        
        # Save to database
        return await self.application_repository.create(application)
    
    async def get_by_id(self, id: UUID) -> Optional[Application]:
        """Get application by ID."""
        return await self.application_repository.get_by_id(id)
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Application]:
        """Get all applications with pagination."""
        return await self.application_repository.get_all(skip=skip, limit=limit)
    
    async def get_by_applicant(self, applicant_id: UUID, skip: int = 0, limit: int = 100) -> List[Application]:
        """Get applications by applicant."""
        return await self.application_repository.get_by_applicant(applicant_id, skip=skip, limit=limit)
    
    async def get_by_job(self, job_id: UUID, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Application]:
        """Get applications by job (company only)."""
        # Verify user owns the job
        job = await self.job_repository.get_by_id(job_id)
        if not job:
            raise NotFoundError(f"Job with ID {job_id} not found")
        
        if job.created_by != user_id:
            raise AuthorizationError("Unauthorized access")
        
        return await self.application_repository.get_by_job(job_id, skip=skip, limit=limit)
    
    async def search_applications(self, filters: ApplicationFilter, user_id: UUID) -> List[Application]:
        """Search applications with filters."""
        # Verify user is an applicant
        user = await self.user_repository.get_by_id(user_id)
        if not user or user.role != UserRole.APPLICANT:
            raise AuthorizationError("Only applicants can search their applications")
        
        return await self.application_repository.search_applications(
            applicant_id=user_id,
            status=filters.application_status[0] if filters.application_status else None,
            skip=(filters.page_number - 1) * filters.page_size,
            limit=filters.page_size
        )
    
    async def update_status(self, id: UUID, obj_in: ApplicationUpdate, user_id: UUID) -> Optional[Application]:
        """Update application status (company only)."""
        application = await self.application_repository.get_by_id(id)
        if not application:
            raise NotFoundError(f"Application with ID {id} not found")
        
        # Verify user owns the job
        job = await self.job_repository.get_by_id(application.job_id)
        if not job or job.created_by != user_id:
            raise AuthorizationError("Unauthorized access")
        
        # Update status
        application.update_status(obj_in.status)
        
        # Save to database
        return await self.application_repository.update(id, application)
    
    async def delete(self, id: UUID) -> bool:
        """Delete application."""
        return await self.application_repository.delete(id)
    
    async def count_by_job(self, job_id: UUID) -> int:
        """Count applications by job."""
        return await self.application_repository.count_by_job(job_id) 