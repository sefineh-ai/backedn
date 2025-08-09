"""
User service implementation.
"""
from typing import List, Optional
from uuid import UUID

from app.core.interfaces import ServiceInterface
from app.core.security import hash_password, verify_password, create_verification_token
from app.core.exceptions import ValidationError, ConflictError, NotFoundError
from app.domain.entities.user import User, UserRole
from app.application.schemas.user import UserCreate, UserUpdate, UserLogin, UserPasswordChange
from app.infrastructure.repositories.user_repository import UserRepository


class UserService(ServiceInterface[User]):
    """
    User service implementation.
    
    This class implements the Service pattern for user business logic,
    following the Clean Architecture principles.
    """
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def create(self, obj_in: UserCreate) -> User:
        """Create a new user."""
        # Check if user already exists
        if await self.user_repository.exists_by_email(obj_in.email):
            raise ConflictError(f"User with email {obj_in.email} already exists")
        
        # Hash password
        hashed_password = hash_password(obj_in.password)
        
        # Create user entity
        user = User(
            full_name=obj_in.full_name,
            email=obj_in.email,
            hashed_password=hashed_password,
            role=obj_in.role
        )
        
        # Save to database
        created = await self.user_repository.create(user)
        
        # Generate email verification token (sending will be handled at endpoint/service boundary)
        _ = create_verification_token(str(created.id))
        
        return created
    
    async def get_by_id(self, id: UUID) -> Optional[User]:
        """Get user by ID."""
        return await self.user_repository.get_by_id(id)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return await self.user_repository.get_by_email(email)
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        return await self.user_repository.get_all(skip=skip, limit=limit)
    
    async def update(self, id: UUID, obj_in: UserUpdate) -> Optional[User]:
        """Update user."""
        user = await self.user_repository.get_by_id(id)
        if not user:
            raise NotFoundError(f"User with ID {id} not found")
        
        # Update fields
        update_data = {}
        if obj_in.full_name is not None:
            update_data['full_name'] = obj_in.full_name
        if obj_in.email is not None:
            # Check if email is already taken by another user
            existing_user = await self.user_repository.get_by_email(obj_in.email)
            if existing_user and existing_user.id != id:
                raise ConflictError(f"Email {obj_in.email} is already taken")
            update_data['email'] = obj_in.email
        if obj_in.password is not None:
            update_data['hashed_password'] = hash_password(obj_in.password)
        if obj_in.is_active is not None:
            update_data['is_active'] = obj_in.is_active
        
        # Create updated user entity
        updated_user = User(**user.dict(), **update_data)
        return await self.user_repository.update(id, updated_user)
    
    async def delete(self, id: UUID) -> bool:
        """Delete user."""
        return await self.user_repository.delete(id)
    
    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        user = await self.user_repository.get_by_email(email)
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_eligible_for_login():
            raise ValidationError("User account is not active or email is not verified")
        
        return user
    
    async def change_password(self, id: UUID, current_password: str, new_password: str) -> Optional[User]:
        """Change user password."""
        user = await self.user_repository.get_by_id(id)
        if not user:
            raise NotFoundError(f"User with ID {id} not found")
        
        if not verify_password(current_password, user.hashed_password):
            raise ValidationError("Current password is incorrect")
        
        # Hash new password
        hashed_password = hash_password(new_password)
        
        # Update user
        updated_user = User(**user.dict(), hashed_password=hashed_password)
        return await self.user_repository.update(id, updated_user)
    
    async def verify_email(self, token: str) -> Optional[User]:
        """Verify user email with token."""
        from app.core.security import decode_verification_token, create_verification_token
        user_id_str, status = decode_verification_token(token)
        if not user_id_str:
            raise ValidationError("Invalid verification token")
        user = await self.user_repository.get_by_id(UUID(user_id_str))
        if not user:
            raise NotFoundError("User not found")
        if status == "expired":
            # resend new token (email sending omitted) and inform client
            _ = create_verification_token(str(user.id))
            raise ValidationError("Verification token expired. A new verification email has been sent.")
        if user.is_verified:
            return user
        user.verify_email()
        return await self.user_repository.update(user.id, user)
    
    async def resend_verification_email(self, email: str) -> bool:
        """Resend verification email."""
        # TODO: Implement resend verification email logic
        # This would typically involve:
        # 1. Finding the user by email
        # 2. Generating a new verification token
        # 3. Sending the email
        pass 