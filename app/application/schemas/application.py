"""
Application schemas for API requests and responses.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from app.domain.entities.application import ApplicationStatus


class ApplicationBase(BaseModel):
    """Base application schema."""
    
    job_id: UUID = Field(..., description="Job ID")
    resume_link: str = Field(..., description="URL to Cloudinary resume file")
    cover_letter: Optional[str] = Field(None, max_length=200, description="Cover letter")


class ApplicationCreate(ApplicationBase):
    """Schema for creating an application."""
    
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


class ApplicationUpdate(BaseModel):
    """Schema for updating an application."""
    
    status: ApplicationStatus = Field(..., description="Application status")


class ApplicationResponse(ApplicationBase):
    """Schema for application response."""
    
    id: UUID = Field(description="Application unique identifier")
    applicant_id: UUID = Field(description="Applicant user ID")
    status: ApplicationStatus = Field(description="Application status")
    applied_at: datetime = Field(description="Application timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    applicant_name: Optional[str] = Field(None, description="Applicant name")
    job_title: Optional[str] = Field(None, description="Job title")
    company_name: Optional[str] = Field(None, description="Company name")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class ApplicationListResponse(BaseModel):
    """Schema for application list response."""
    
    applications: list[ApplicationResponse] = Field(description="List of applications")
    total: int = Field(description="Total number of applications")
    skip: int = Field(description="Number of records skipped")
    limit: int = Field(description="Maximum number of records returned")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class ApplicationFilter(BaseModel):
    """Schema for application filtering."""
    
    company_name: Optional[str] = Field(None, description="Company name filter")
    job_status: Optional[str] = Field(None, description="Job status filter (Open or Closed)")
    application_status: Optional[list[ApplicationStatus]] = Field(None, description="Application status filter")
    sort_by: Optional[str] = Field(default="applied_at", description="Sort by field")
    sort_order: Optional[str] = Field(default="desc", description="Sort order (asc or desc)")
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