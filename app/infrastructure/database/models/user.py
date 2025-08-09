"""
User database model.
"""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, String, Enum
from sqlalchemy.orm import relationship

from app.domain.entities.user import UserRole
from app.infrastructure.database.base import Base


class UserModel(Base):
    """
    User database model.
    
    This class represents the user table in the database,
    following SQLAlchemy ORM patterns.
    """
    
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()), index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    jobs = relationship("JobModel", back_populates="creator", cascade="all, delete-orphan")
    applications = relationship("ApplicationModel", back_populates="applicant", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<UserModel(id={self.id}, email={self.email}, full_name={self.full_name})>"   