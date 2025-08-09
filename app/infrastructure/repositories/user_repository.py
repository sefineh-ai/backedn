"""
User repository implementation.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.interfaces import RepositoryInterface
from app.domain.entities.user import User, UserRole
from app.infrastructure.database.models.user import UserModel


class UserRepository(RepositoryInterface[User]):
    """
    User repository implementation.
    
    This class implements the Repository pattern for user data access,
    following the Clean Architecture principles.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create(self, obj_in: User) -> User:
        """Create a new user."""
        db_obj = UserModel(
            id=str(obj_in.id),
            full_name=obj_in.full_name,
            email=obj_in.email,
            hashed_password=obj_in.hashed_password,
            role=obj_in.role,
            is_active=obj_in.is_active,
            is_verified=obj_in.is_verified,
            created_at=obj_in.created_at,
            updated_at=obj_in.updated_at
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return self._to_entity(db_obj)
    
    async def get_by_id(self, id: UUID) -> Optional[User]:
        """Get user by ID."""
        db_obj = self.db.query(UserModel).filter(UserModel.id == str(id)).first()
        return self._to_entity(db_obj) if db_obj else None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        db_obj = self.db.query(UserModel).filter(UserModel.email == email).first()
        return self._to_entity(db_obj) if db_obj else None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        db_objs = self.db.query(UserModel).offset(skip).limit(limit).all()
        return [self._to_entity(db_obj) for db_obj in db_objs]
    
    async def update(self, id: UUID, obj_in: User) -> Optional[User]:
        """Update user."""
        db_obj = self.db.query(UserModel).filter(UserModel.id == str(id)).first()
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
        """Delete user."""
        db_obj = self.db.query(UserModel).filter(UserModel.id == str(id)).first()
        if not db_obj:
            return False
        
        self.db.delete(db_obj)
        self.db.commit()
        return True
    
    async def exists(self, id: UUID) -> bool:
        """Check if user exists."""
        return self.db.query(UserModel).filter(UserModel.id == str(id)).first() is not None
    
    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email."""
        return self.db.query(UserModel).filter(UserModel.email == email).first() is not None
    
    def _to_entity(self, db_obj: UserModel) -> User:
        """Convert database model to domain entity."""
        return User(
            id=UUID(db_obj.id),
            full_name=db_obj.full_name,
            email=db_obj.email,
            hashed_password=db_obj.hashed_password,
            role=db_obj.role,
            is_active=db_obj.is_active,
            is_verified=db_obj.is_verified,
            created_at=db_obj.created_at,
            updated_at=db_obj.updated_at
        ) 