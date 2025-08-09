"""
Application database model.
"""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, String, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.domain.entities.application import ApplicationStatus
from app.infrastructure.database.base import Base


class ApplicationModel(Base):
    """
    Application database model.
    
    This class represents the application table in the database,
    following SQLAlchemy ORM patterns.
    """
    
    __tablename__ = "applications"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()), index=True)
    applicant_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False, index=True)
    resume_link = Column(String(500), nullable=False)
    cover_letter = Column(Text, nullable=True)
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.APPLIED, nullable=False)
    applied_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    applicant = relationship("UserModel", back_populates="applications")
    job = relationship("JobModel", back_populates="applications")
    
    def __repr__(self) -> str:
        return f"<ApplicationModel(id={self.id}, applicant_id={self.applicant_id}, job_id={self.job_id}, status={self.status})>" 