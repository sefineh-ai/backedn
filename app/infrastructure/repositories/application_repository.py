"""
Application repository implementation.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.interfaces import RepositoryInterface
from app.domain.entities.application import Application, ApplicationStatus
from app.infrastructure.database.models.application import ApplicationModel
from app.infrastructure.database.models.user import UserModel
from app.infrastructure.database.models.job import JobModel


class ApplicationRepository(RepositoryInterface[Application]):
    """
    Application repository implementation.
    
    This class implements the Repository pattern for application data access,
    following the Clean Architecture principles.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create(self, obj_in: Application) -> Application:
        """Create a new application."""
        db_obj = ApplicationModel(
            id=str(obj_in.id),
            applicant_id=str(obj_in.applicant_id),
            job_id=str(obj_in.job_id),
            resume_link=obj_in.resume_link,
            cover_letter=obj_in.cover_letter,
            status=obj_in.status,
            applied_at=obj_in.applied_at,
            updated_at=obj_in.updated_at
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return self._to_entity(db_obj)
    
    async def get_by_id(self, id: UUID) -> Optional[Application]:
        """Get application by ID."""
        db_obj = self.db.query(ApplicationModel).filter(ApplicationModel.id == str(id)).first()
        return self._to_entity(db_obj) if db_obj else None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Application]:
        """Get all applications with pagination."""
        db_objs = self.db.query(ApplicationModel).offset(skip).limit(limit).all()
        return [self._to_entity(db_obj) for db_obj in db_objs]
    
    async def get_by_applicant(self, applicant_id: UUID, skip: int = 0, limit: int = 100) -> List[Application]:
        """Get applications by applicant."""
        db_objs = self.db.query(ApplicationModel).filter(ApplicationModel.applicant_id == str(applicant_id)).offset(skip).limit(limit).all()
        return [self._to_entity(db_obj) for db_obj in db_objs]
    
    async def get_by_job(self, job_id: UUID, skip: int = 0, limit: int = 100) -> List[Application]:
        """Get applications by job."""
        db_objs = self.db.query(ApplicationModel).filter(ApplicationModel.job_id == str(job_id)).offset(skip).limit(limit).all()
        return [self._to_entity(db_obj) for db_obj in db_objs]
    
    async def get_by_applicant_and_job(self, applicant_id: UUID, job_id: UUID) -> Optional[Application]:
        """Get application by applicant and job."""
        db_obj = self.db.query(ApplicationModel).filter(
            and_(ApplicationModel.applicant_id == str(applicant_id), ApplicationModel.job_id == str(job_id))
        ).first()
        return self._to_entity(db_obj) if db_obj else None
    
    async def search_applications(self, applicant_id: Optional[UUID] = None, job_id: Optional[UUID] = None,
                                status: Optional[ApplicationStatus] = None, skip: int = 0, limit: int = 100) -> List[Application]:
        """Search applications with filters."""
        query = self.db.query(ApplicationModel)
        
        if applicant_id:
            query = query.filter(ApplicationModel.applicant_id == str(applicant_id))
        if job_id:
            query = query.filter(ApplicationModel.job_id == str(job_id))
        if status:
            query = query.filter(ApplicationModel.status == status)
        
        db_objs = query.offset(skip).limit(limit).all()
        return [self._to_entity(db_obj) for db_obj in db_objs]
    
    async def update(self, id: UUID, obj_in: Application) -> Optional[Application]:
        """Update application."""
        db_obj = self.db.query(ApplicationModel).filter(ApplicationModel.id == str(id)).first()
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
        """Delete application."""
        db_obj = self.db.query(ApplicationModel).filter(ApplicationModel.id == str(id)).first()
        if not db_obj:
            return False
        
        self.db.delete(db_obj)
        self.db.commit()
        return True
    
    async def exists(self, id: UUID) -> bool:
        """Check if application exists."""
        return self.db.query(ApplicationModel).filter(ApplicationModel.id == str(id)).first() is not None
    
    async def exists_by_applicant_and_job(self, applicant_id: UUID, job_id: UUID) -> bool:
        """Check if application exists by applicant and job."""
        return self.db.query(ApplicationModel).filter(
            and_(ApplicationModel.applicant_id == str(applicant_id), ApplicationModel.job_id == str(job_id))
        ).first() is not None
    
    async def count_by_job(self, job_id: UUID) -> int:
        """Count applications by job."""
        return self.db.query(ApplicationModel).filter(ApplicationModel.job_id == str(job_id)).count()
    
    def _to_entity(self, db_obj: ApplicationModel) -> Application:
        """Convert database model to domain entity."""
        return Application(
            id=UUID(db_obj.id),
            applicant_id=UUID(db_obj.applicant_id),
            job_id=UUID(db_obj.job_id),
            resume_link=db_obj.resume_link,
            cover_letter=db_obj.cover_letter,
            status=db_obj.status,
            applied_at=db_obj.applied_at,
            updated_at=db_obj.updated_at
        ) 