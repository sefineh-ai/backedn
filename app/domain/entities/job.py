"""
Job domain entity.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class JobStatus(str, Enum):
    """Job status enumeration."""
    DRAFT = "Draft"
    OPEN = "Open"
    CLOSED = "Closed"


class Job(BaseModel):
    """
    Job domain entity.
    
    This class represents a job in the domain layer,
    following the Domain-Driven Design principles.
    """
    
    id: UUID = Field(default_factory=uuid4, description="Job unique identifier")
    title: str = Field(..., min_length=1, max_length=100, description="Job title")
    description: str = Field(..., min_length=20, max_length=2000, description="Job description")
    location: Optional[str] = Field(None, description="Job location")
    status: JobStatus = Field(default=JobStatus.DRAFT, description="Job status")
    created_by: UUID = Field(..., description="User ID who created the job")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    @validator('title')
    def validate_title(cls, v: str) -> str:
        """Validate job title."""
        if len(v.strip()) < 1:
            raise ValueError('Job title cannot be empty')
        if len(v.strip()) > 100:
            raise ValueError('Job title cannot exceed 100 characters')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v: str) -> str:
        """Validate job description."""
        if len(v.strip()) < 20:
            raise ValueError('Job description must be at least 20 characters long')
        if len(v.strip()) > 2000:
            raise ValueError('Job description cannot exceed 2000 characters')
        return v.strip()
    
    def update_status(self, new_status: JobStatus) -> None:
        """Update job status with forward-only flow validation."""
        # Define the allowed status transitions
        allowed_transitions = {
            JobStatus.DRAFT: [JobStatus.OPEN],
            JobStatus.OPEN: [JobStatus.CLOSED],
            JobStatus.CLOSED: []  # No further transitions allowed
        }
        
        if new_status not in allowed_transitions.get(self.status, []):
            raise ValueError(f'Invalid status transition from {self.status} to {new_status}')
        
        self.status = new_status
        self.updated_at = datetime.utcnow()
    
    def update_details(self, title: Optional[str] = None, description: Optional[str] = None, location: Optional[str] = None) -> None:
        """Update job details."""
        if title is not None:
            self.title = title.strip()
        if description is not None:
            self.description = description.strip()
        if location is not None:
            self.location = location.strip() if location else None
        
        self.updated_at = datetime.utcnow()
    
    def is_open(self) -> bool:
        """Check if job is open for applications."""
        return self.status == JobStatus.OPEN
    
    def is_closed(self) -> bool:
        """Check if job is closed."""
        return self.status == JobStatus.CLOSED
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        } 