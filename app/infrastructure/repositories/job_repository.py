"""
Job repository implementation.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.interfaces import RepositoryInterface
from app.domain.entities.job import Job, JobStatus
from app.infrastructure.database.models.job import JobModel
from app.infrastructure.database.models.user import UserModel


class JobRepository(RepositoryInterface[Job]):
    """
    Job repository implementation.
    
    This class implements the Repository pattern for job data access,
    following the Clean Architecture principles.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create(self, obj_in: Job) -> Job:
        """Create a new job."""
        db_obj = JobModel(
            id=str(obj_in.id),
            title=obj_in.title,
            description=obj_in.description,
            location=obj_in.location,
            status=obj_in.status,
            created_by=str(obj_in.created_by),
            created_at=obj_in.created_at,
            updated_at=obj_in.updated_at
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return self._to_entity(db_obj)
    
    async def get_by_id(self, id: UUID) -> Optional[Job]:
        """Get job by ID."""
        db_obj = self.db.query(JobModel).filter(JobModel.id == str(id)).first()
        return self._to_entity(db_obj) if db_obj else None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Job]:
        """Get all jobs with pagination."""
        db_objs = self.db.query(JobModel).offset(skip).limit(limit).all()
        return [self._to_entity(db_obj) for db_obj in db_objs]
    
    async def get_by_creator(self, creator_id: UUID, skip: int = 0, limit: int = 100) -> List[Job]:
        """Get jobs by creator."""
        db_objs = self.db.query(JobModel).filter(JobModel.created_by == str(creator_id)).offset(skip).limit(limit).all()
        return [self._to_entity(db_obj) for db_obj in db_objs]
    
    async def search_jobs(self, title: Optional[str] = None, location: Optional[str] = None, 
                         company_name: Optional[str] = None, status: Optional[JobStatus] = None,
                         skip: int = 0, limit: int = 100) -> List[Job]:
        """Search jobs with filters."""
        query = self.db.query(JobModel).join(UserModel, JobModel.created_by == UserModel.id)
        
        if title:
            query = query.filter(JobModel.title.ilike(f"%{title}%"))
        if location:
            query = query.filter(JobModel.location.ilike(f"%{location}%"))
        if company_name:
            query = query.filter(UserModel.full_name.ilike(f"%{company_name}%"))
        if status:
            query = query.filter(JobModel.status == status)
        
        db_objs = query.offset(skip).limit(limit).all()
        return [self._to_entity(db_obj) for db_obj in db_objs]
    
    async def update(self, id: UUID, obj_in: Job) -> Optional[Job]:
        """Update job."""
        db_obj = self.db.query(JobModel).filter(JobModel.id == str(id)).first()
        if not db_obj:
            return None
        
        # Update fields
        for field, value in obj_in.dict(exclude_unset=True).items():
            if field != 'id':
                setattr(db_obj, field, value)
        
        self.db.commit()
        self.db.refresh(db_obj)
        return self._to_entity(db_obj)
    
    async def delete(self, id: UUID) -> bool:
        """Delete job."""
        db_obj = self.db.query(JobModel).filter(JobModel.id == str(id)).first()
        if not db_obj:
            return False
        
        self.db.delete(db_obj)
        self.db.commit()
        return True
    
    async def exists(self, id: UUID) -> bool:
        """Check if job exists."""
        return self.db.query(JobModel).filter(JobModel.id == str(id)).first() is not None
    
    async def count_by_creator(self, creator_id: UUID) -> int:
        """Count jobs by creator."""
        return self.db.query(JobModel).filter(JobModel.created_by == str(creator_id)).count()
    
    def _to_entity(self, db_obj: JobModel) -> Job:
        """Convert database model to domain entity."""
        return Job(
            id=UUID(db_obj.id),
            title=db_obj.title,
            description=db_obj.description,
            location=db_obj.location,
            status=db_obj.status,
            created_by=UUID(db_obj.created_by),
            created_at=db_obj.created_at,
            updated_at=db_obj.updated_at
        ) 