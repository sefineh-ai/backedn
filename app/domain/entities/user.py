"""
User domain entity.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field, validator


class UserRole(str, Enum):
    """User role enumeration."""
    APPLICANT = "applicant"
    COMPANY = "company"


class User(BaseModel):
    """
    User domain entity.
    
    This class represents a user in the domain layer,
    following the Domain-Driven Design principles.
    """
    
    id: UUID = Field(default_factory=uuid4, description="User unique identifier")
    full_name: str = Field(..., min_length=1, max_length=100, description="Full name")
    email: EmailStr = Field(description="User email address")
    hashed_password: Optional[str] = Field(None, description="Hashed password")
    role: UserRole = Field(..., description="User role (applicant or company)")
    is_active: bool = Field(default=True, description="User active status")
    is_verified: bool = Field(default=False, description="Email verification status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
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
    
    def activate(self) -> None:
        """Activate the user."""
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        """Deactivate the user."""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def verify_email(self) -> None:
        """Mark email as verified."""
        self.is_verified = True
        self.updated_at = datetime.utcnow()
    
    def update_full_name(self, full_name: str) -> None:
        """Update user's full name."""
        if len(full_name.strip()) < 1:
            raise ValueError('Full name cannot be empty')
        self.full_name = full_name.strip()
        self.updated_at = datetime.utcnow()
    
    def set_password(self, hashed_password: str) -> None:
        """Set hashed password."""
        self.hashed_password = hashed_password
        self.updated_at = datetime.utcnow()
    
    def is_eligible_for_login(self) -> bool:
        """Check if user is eligible for login."""
        return self.is_active and self.is_verified
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        } 