"""
User schemas for API requests and responses.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, validator

from app.domain.entities.user import UserRole


class UserBase(BaseModel):
    """Base user schema."""
    
    full_name: str = Field(..., min_length=1, max_length=100, description="Full name")
    email: EmailStr = Field(description="User email address")
    role: UserRole = Field(..., description="User role (applicant or company)")


class UserCreate(UserBase):
    """Schema for creating a user."""
    
    password: str = Field(..., min_length=8, description="User password")
    
    @validator('password')
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v):
            raise ValueError('Password must contain at least one special character')
        return v
    
    @validator('full_name')
    def validate_full_name(cls, v: str) -> str:
        """Validate full name format - only alphabets and one space between first and last name."""
        v = v.strip()
        if len(v) < 1:
            raise ValueError('Full name cannot be empty')
        
        # Check if name contains only alphabets and spaces
        if not all(c.isalpha() or c.isspace() for c in v):
            raise ValueError('Full name must contain only alphabets and spaces')
        
        # Check for exactly one space between first and last name
        name_parts = v.split()
        if len(name_parts) != 2:
            raise ValueError('Full name must contain exactly two parts (first name and last name)')
        
        # Check if each part contains only alphabets
        if not all(part.isalpha() for part in name_parts):
            raise ValueError('First name and last name must contain only alphabets')
        
        return v


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    
    full_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Full name")
    email: Optional[EmailStr] = Field(None, description="User email address")
    password: Optional[str] = Field(None, min_length=8, description="User password")
    is_active: Optional[bool] = Field(None, description="User active status")
    
    @validator('password')
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        """Validate password strength if provided."""
        if v is not None:
            if len(v) < 8:
                raise ValueError('Password must be at least 8 characters long')
            if not any(c.isupper() for c in v):
                raise ValueError('Password must contain at least one uppercase letter')
            if not any(c.islower() for c in v):
                raise ValueError('Password must contain at least one lowercase letter')
            if not any(c.isdigit() for c in v):
                raise ValueError('Password must contain at least one digit')
            if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v):
                raise ValueError('Password must contain at least one special character')
        return v
    
    @validator('full_name')
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate full name format if provided."""
        if v is not None:
            v = v.strip()
            if len(v) < 1:
                raise ValueError('Full name cannot be empty')
            
            # Check if name contains only alphabets and spaces
            if not all(c.isalpha() or c.isspace() for c in v):
                raise ValueError('Full name must contain only alphabets and spaces')
            
            # Check for exactly one space between first and last name
            name_parts = v.split()
            if len(name_parts) != 2:
                raise ValueError('Full name must contain exactly two parts (first name and last name)')
            
            # Check if each part contains only alphabets
            if not all(part.isalpha() for part in name_parts):
                raise ValueError('First name and last name must contain only alphabets')
        
        return v


class UserResponse(UserBase):
    """Schema for user response."""
    
    id: UUID = Field(description="User unique identifier")
    is_active: bool = Field(description="User active status")
    is_verified: bool = Field(description="Email verification status")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class UserListResponse(BaseModel):
    """Schema for user list response."""
    
    users: list[UserResponse] = Field(description="List of users")
    total: int = Field(description="Total number of users")
    skip: int = Field(description="Number of records skipped")
    limit: int = Field(description="Maximum number of records returned")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class UserLogin(BaseModel):
    """Schema for user login."""
    
    email: EmailStr = Field(description="User email address")
    password: str = Field(..., description="User password")


class UserPasswordChange(BaseModel):
    """Schema for password change."""
    
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    
    @validator('new_password')
    def validate_new_password(cls, v: str) -> str:
        """Validate new password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v):
            raise ValueError('Password must contain at least one special character')
        return v


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