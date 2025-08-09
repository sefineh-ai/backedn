"""
Job service implementation.
"""
from typing import List, Optional
from uuid import UUID

from app.core.interfaces import ServiceInterface
from app.core.exceptions import ValidationError, ConflictError, NotFoundError, AuthorizationError
from app.domain.entities.job import Job, JobStatus
from app.domain.entities.user import UserRole
from app.application.schemas.job import JobCreate, JobUpdate, JobFilter
from app.infrastructure.repositories.job_repository import JobRepository
from app.infrastructure.repositories.user_repository import UserRepository


class JobService(ServiceInterface[Job]):
    """
    Job service implementation.
    
    This class implements the Service pattern for job business logic,
    following the Clean Architecture principles.
    """
    
    def __init__(self, job_repository: JobRepository, user_repository: UserRepository):
        self.job_repository = job_repository
        self.user_repository = user_repository
    
    async def create(self, obj_in: JobCreate, creator_id: UUID) -> Job:
        """Create a new job."""
        # Verify creator is a company
        creator = await self.user_repository.get_by_id(creator_id)
        if not creator:
            raise NotFoundError(f"User with ID {creator_id} not found")
        
        if creator.role != UserRole.COMPANY:
            raise AuthorizationError("Only companies can create jobs")
        
        # Create job entity
        job = Job(
            title=obj_in.title,
            description=obj_in.description,
            location=obj_in.location,
            status=obj_in.status or JobStatus.DRAFT,
            created_by=creator_id
        )
        
        # Save to database
        return await self.job_repository.create(job)
    
    async def get_by_id(self, id: UUID) -> Optional[Job]:
        """Get job by ID."""
        return await self.job_repository.get_by_id(id)
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Job]:
        """Get all jobs with pagination."""
        return await self.job_repository.get_all(skip=skip, limit=limit)
    
    async def get_by_creator(self, creator_id: UUID, skip: int = 0, limit: int = 100) -> List[Job]:
        """Get jobs by creator."""
        return await self.job_repository.get_by_creator(creator_id, skip=skip, limit=limit)
    
    async def search_jobs(self, filters: JobFilter) -> List[Job]:
        """Search jobs with filters."""
        return await self.job_repository.search_jobs(
            title=filters.title,
            location=filters.location,
            company_name=filters.company_name,
            status=filters.status,
            skip=(filters.page_number - 1) * filters.page_size,
            limit=filters.page_size
        )
    
    async def update(self, id: UUID, obj_in: JobUpdate, user_id: UUID) -> Optional[Job]:
        """Update job."""
        job = await self.job_repository.get_by_id(id)
        if not job:
            raise NotFoundError(f"Job with ID {id} not found")
        
        # Check if user owns the job
        if job.created_by != user_id:
            raise AuthorizationError("Unauthorized access")
        
        # Verify user is a company
        user = await self.user_repository.get_by_id(user_id)
        if not user or user.role != UserRole.COMPANY:
            raise AuthorizationError("Only companies can update jobs")
        
        # Update fields
        update_data = {}
        if obj_in.title is not None:
            update_data['title'] = obj_in.title
        if obj_in.description is not None:
            update_data['description'] = obj_in.description
        if obj_in.location is not None:
            update_data['location'] = obj_in.location
        if obj_in.status is not None:
            # Validate status transition
            try:
                job.update_status(obj_in.status)
                update_data['status'] = obj_in.status
            except ValueError as e:
                raise ValidationError(str(e))
        
        # Create updated job entity
        updated_job = Job(**job.dict(), **update_data)
        return await self.job_repository.update(id, updated_job)
    
    async def delete(self, id: UUID, user_id: UUID) -> bool:
        """Delete job."""
        job = await self.job_repository.get_by_id(id)
        if not job:
            raise NotFoundError(f"Job with ID {id} not found")
        
        # Check if user owns the job
        if job.created_by != user_id:
            raise AuthorizationError("Unauthorized access")
        
        return await self.job_repository.delete(id)
    
    async def count_by_creator(self, creator_id: UUID) -> int:
        """Count jobs by creator."""
        return await self.job_repository.count_by_creator(creator_id) 