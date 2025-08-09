"""
Job database model.
"""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, String, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.domain.entities.job import JobStatus
from app.infrastructure.database.base import Base


class JobModel(Base):
    """
    Job database model.
    
    This class represents the job table in the database,
    following SQLAlchemy ORM patterns.
    """
    
    __tablename__ = "jobs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()), index=True)
    title = Column(String(100), nullable=False, index=True)
    description = Column(String(2000), nullable=False)
    location = Column(String(255), nullable=True)
    status = Column(Enum(JobStatus), default=JobStatus.DRAFT, nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    creator = relationship("UserModel", back_populates="jobs")
    applications = relationship("ApplicationModel", back_populates="job", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<JobModel(id={self.id}, title={self.title}, status={self.status})>" 