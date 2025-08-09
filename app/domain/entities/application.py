"""
Application domain entity.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class ApplicationStatus(str, Enum):
    """Application status enumeration."""
    APPLIED = "Applied"
    REVIEWED = "Reviewed"
    INTERVIEW = "Interview"
    REJECTED = "Rejected"
    HIRED = "Hired"


class Application(BaseModel):
    """
    Application domain entity.
    
    This class represents a job application in the domain layer,
    following the Domain-Driven Design principles.
    """
    
    id: UUID = Field(default_factory=uuid4, description="Application unique identifier")
    applicant_id: UUID = Field(..., description="Applicant user ID")
    job_id: UUID = Field(..., description="Job ID")
    resume_link: str = Field(..., description="URL to Cloudinary resume file")
    cover_letter: Optional[str] = Field(None, max_length=200, description="Cover letter")
    status: ApplicationStatus = Field(default=ApplicationStatus.APPLIED, description="Application status")
    applied_at: datetime = Field(default_factory=datetime.utcnow, description="Application timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    @validator('resume_link')
    def validate_resume_link(cls, v: str) -> str:
        """Validate resume link URL."""
        if not v.strip():
            raise ValueError('Resume link cannot be empty')
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Resume link must be a valid URL')
        return v.strip()
    
    @validator('cover_letter')
    def validate_cover_letter(cls, v: Optional[str]) -> Optional[str]:
        """Validate cover letter length."""
        if v is not None and len(v.strip()) > 200:
            raise ValueError('Cover letter cannot exceed 200 characters')
        return v.strip() if v else None
    
    def update_status(self, new_status: ApplicationStatus) -> None:
        """Update application status."""
        self.status = new_status
        self.updated_at = datetime.utcnow()
    
    def is_pending(self) -> bool:
        """Check if application is pending (Applied or Reviewed)."""
        return self.status in [ApplicationStatus.APPLIED, ApplicationStatus.REVIEWED]
    
    def is_active(self) -> bool:
        """Check if application is active (not Rejected or Hired)."""
        return self.status not in [ApplicationStatus.REJECTED, ApplicationStatus.HIRED]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        } 