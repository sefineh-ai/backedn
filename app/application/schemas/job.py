"""
Job schemas for API requests and responses.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from app.domain.entities.job import JobStatus


class JobBase(BaseModel):
    """Base job schema."""
    
    title: str = Field(..., min_length=1, max_length=100, description="Job title")
    description: str = Field(..., min_length=20, max_length=2000, description="Job description")
    location: Optional[str] = Field(None, description="Job location")


class JobCreate(JobBase):
    """Schema for creating a job."""
    
    status: Optional[JobStatus] = Field(default=JobStatus.DRAFT, description="Job status")
    
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


class JobUpdate(BaseModel):
    """Schema for updating a job."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="Job title")
    description: Optional[str] = Field(None, min_length=20, max_length=2000, description="Job description")
    location: Optional[str] = Field(None, description="Job location")
    status: Optional[JobStatus] = Field(None, description="Job status")
    
    @validator('title')
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate job title if provided."""
        if v is not None:
            if len(v.strip()) < 1:
                raise ValueError('Job title cannot be empty')
            if len(v.strip()) > 100:
                raise ValueError('Job title cannot exceed 100 characters')
            return v.strip()
        return v
    
    @validator('description')
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate job description if provided."""
        if v is not None:
            if len(v.strip()) < 20:
                raise ValueError('Job description must be at least 20 characters long')
            if len(v.strip()) > 2000:
                raise ValueError('Job description cannot exceed 2000 characters')
            return v.strip()
        return v


class JobResponse(JobBase):
    """Schema for job response."""
    
    id: UUID = Field(description="Job unique identifier")
    status: JobStatus = Field(description="Job status")
    created_by: UUID = Field(description="User ID who created the job")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    company_name: Optional[str] = Field(None, description="Company name")
    application_count: Optional[int] = Field(0, description="Number of applications")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class JobListResponse(BaseModel):
    """Schema for job list response."""
    
    jobs: list[JobResponse] = Field(description="List of jobs")
    total: int = Field(description="Total number of jobs")
    skip: int = Field(description="Number of records skipped")
    limit: int = Field(description="Maximum number of records returned")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class JobFilter(BaseModel):
    """Schema for job filtering."""
    
    title: Optional[str] = Field(None, description="Job title filter")
    location: Optional[str] = Field(None, description="Job location filter")
    company_name: Optional[str] = Field(None, description="Company name filter")
    status: Optional[JobStatus] = Field(None, description="Job status filter")
    page_number: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=10, ge=1, le=100, description="Page size")


# Base response structure
class BaseResponse(BaseModel):
    """Base response structure."""
    
    success: bool = Field(description="Success status")
    message: str = Field(description="Response message")
    object: Optional[dict] = Field(None, description="Response object")
    errors: Optional[list[str]] = Field(None, description="List of errors")


class PaginatedResponse(BaseModel):
    """Paginated response structure."""
    
    success: bool = Field(description="Success status")
    message: str = Field(description="Response message")
    object: list = Field(description="List of objects")
    page_number: int = Field(description="Current page number")
    page_size: int = Field(description="Page size")
    total_size: int = Field(description="Total number of items")
    errors: Optional[list[str]] = Field(None, description="List of errors") 