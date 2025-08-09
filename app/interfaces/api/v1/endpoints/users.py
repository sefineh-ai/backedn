"""
User API endpoints.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.application.schemas.user import (
    UserCreate, UserResponse, UserUpdate, UserListResponse, 
    UserLogin, UserPasswordChange, BaseResponse, PaginatedResponse
)
from app.application.services.user_service import UserService
from app.infrastructure.database.base import get_db
from app.infrastructure.repositories.user_repository import UserRepository
from app.core.security import create_access_token, create_verification_token
from app.core.config import settings
from app.core.exceptions import ValidationError, ConflictError, NotFoundError

router = APIRouter()


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Get user service dependency."""
    user_repository = UserRepository(db)
    return UserService(user_repository)


@router.post("/signup", response_model=BaseResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    user_service: UserService = Depends(get_user_service)
) -> BaseResponse:
    """
    Create a new user (signup).
    
    This endpoint allows users to sign up as either a company or applicant.
    """
    try:
        user = await user_service.create(user_in)
        # Build verification link
        verification_token = create_verification_token(str(user.id))
        verify_url = f"{settings.public_base_url}/api/v1/users/verify-email?token={verification_token}"
        return BaseResponse(
            success=True,
            message="User created successfully. Please verify your email using the link sent.",
            object={
                **UserResponse(
                    id=user.id,
                    full_name=user.full_name,
                    email=user.email,
                    role=user.role,
                    is_active=user.is_active,
                    is_verified=user.is_verified,
                    created_at=user.created_at,
                    updated_at=user.updated_at
                ).model_dump(),
                **({
                    "verification_url": verify_url,
                    "verification_token": verification_token
                } if settings.debug else {})
            },
            errors=None
        )
    except (ValidationError, ConflictError) as e:
        return BaseResponse(
            success=False,
            message=str(e),
            object=None,
            errors=[str(e)]
        )


@router.post("/login", response_model=BaseResponse)
async def login_user(
    user_in: UserLogin,
    user_service: UserService = Depends(get_user_service)
) -> BaseResponse:
    """
    User login.
    
    This endpoint allows users to log in with email and password.
    """
    try:
        user = await user_service.authenticate(user_in.email, user_in.password)
        if not user:
            return BaseResponse(
                success=False,
                message="Invalid email or password",
                object=None,
                errors=["Invalid credentials"]
            )
        if not user.is_verified:
            return BaseResponse(
                success=False,
                message="Email not verified. Please verify your email before logging in.",
                object=None,
                errors=["Email not verified"]
            )
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
        
        return BaseResponse(
            success=True,
            message="Login successful",
            object={
                "access_token": access_token,
                "token_type": "bearer",
                "user": UserResponse(
                    id=user.id,
                    full_name=user.full_name,
                    email=user.email,
                    role=user.role,
                    is_active=user.is_active,
                    is_verified=user.is_verified,
                    created_at=user.created_at,
                    updated_at=user.updated_at
                ).dict()
            },
            errors=None
        )
    except ValidationError as e:
        return BaseResponse(
            success=False,
            message=str(e),
            object=None,
            errors=[str(e)]
        )


@router.get("/verify-email", response_model=BaseResponse)
async def verify_email(token: str, user_service: UserService = Depends(get_user_service)) -> BaseResponse:
    try:
        user = await user_service.verify_email(token)
        return BaseResponse(
            success=True,
            message="Email verified successfully",
            object=UserResponse(
                id=user.id,
                full_name=user.full_name,
                email=user.email,
                role=user.role,
                is_active=user.is_active,
                is_verified=user.is_verified,
                created_at=user.created_at,
                updated_at=user.updated_at
            ).dict(),
            errors=None
        )
    except ValidationError as e:
        return BaseResponse(success=False, message=str(e), object=None, errors=[str(e)])
    except NotFoundError as e:
        return BaseResponse(success=False, message=str(e), object=None, errors=[str(e)])


@router.post("/resend-verification", response_model=BaseResponse)
async def resend_verification(email: str, user_service: UserService = Depends(get_user_service)) -> BaseResponse:
    try:
        user = await user_service.get_by_email(email)
        if not user:
            return BaseResponse(success=True, message="If the email exists, a new verification has been sent.", object=None, errors=None)
        if user.is_verified:
            return BaseResponse(success=True, message="Email already verified.", object=None, errors=None)
        token = create_verification_token(str(user.id))
        verify_url = f"{settings.public_base_url}/api/v1/users/verify-email?token={token}"
        obj = {"message": "Verification email resent"}
        if settings.debug:
            obj.update({"verification_url": verify_url, "verification_token": token})
        return BaseResponse(success=True, message="Verification email resent", object=obj, errors=None)
    except Exception as e:
        return BaseResponse(success=False, message="Failed to resend verification", object=None, errors=[str(e)])


@router.get("/{user_id}", response_model=BaseResponse)
async def get_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service)
) -> BaseResponse:
    """
    Get user by ID.
    """
    try:
        user = await user_service.get_by_id(user_id)
        if not user:
            return BaseResponse(
                success=False,
                message="User not found",
                object=None,
                errors=["User not found"]
            )
        
        return BaseResponse(
            success=True,
            message="User retrieved successfully",
            object=UserResponse(
                id=user.id,
                full_name=user.full_name,
                email=user.email,
                role=user.role,
                is_active=user.is_active,
                is_verified=user.is_verified,
                created_at=user.created_at,
                updated_at=user.updated_at
            ).dict(),
            errors=None
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message="Error retrieving user",
            object=None,
            errors=[str(e)]
        )


@router.put("/{user_id}", response_model=BaseResponse)
async def update_user(
    user_id: UUID,
    user_in: UserUpdate,
    user_service: UserService = Depends(get_user_service)
) -> BaseResponse:
    """
    Update user.
    """
    try:
        user = await user_service.update(user_id, user_in)
        if not user:
            return BaseResponse(
                success=False,
                message="User not found",
                object=None,
                errors=["User not found"]
            )
        
        return BaseResponse(
            success=True,
            message="User updated successfully",
            object=UserResponse(
                id=user.id,
                full_name=user.full_name,
                email=user.email,
                role=user.role,
                is_active=user.is_active,
                is_verified=user.is_verified,
                created_at=user.created_at,
                updated_at=user.updated_at
            ).dict(),
            errors=None
        )
    except (ValidationError, ConflictError, NotFoundError) as e:
        return BaseResponse(
            success=False,
            message=str(e),
            object=None,
            errors=[str(e)]
        )


@router.delete("/{user_id}", response_model=BaseResponse)
async def delete_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service)
) -> BaseResponse:
    """
    Delete user.
    """
    try:
        deleted = await user_service.delete(user_id)
        if not deleted:
            return BaseResponse(
                success=False,
                message="User not found",
                object=None,
                errors=["User not found"]
            )
        
        return BaseResponse(
            success=True,
            message="User deleted successfully",
            object=None,
            errors=None
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message="Error deleting user",
            object=None,
            errors=[str(e)]
        )


@router.post("/{user_id}/change-password", response_model=BaseResponse)
async def change_user_password(
    user_id: UUID,
    password_change: UserPasswordChange,
    user_service: UserService = Depends(get_user_service)
) -> BaseResponse:
    """
    Change user password.
    """
    try:
        user = await user_service.change_password(
            user_id, password_change.current_password, password_change.new_password
        )
        if not user:
            return BaseResponse(
                success=False,
                message="User not found",
                object=None,
                errors=["User not found"]
            )
        
        return BaseResponse(
            success=True,
            message="Password changed successfully",
            object=UserResponse(
                id=user.id,
                full_name=user.full_name,
                email=user.email,
                role=user.role,
                is_active=user.is_active,
                is_verified=user.is_verified,
                created_at=user.created_at,
                updated_at=user.updated_at
            ).dict(),
            errors=None
        )
    except (ValidationError, NotFoundError) as e:
        return BaseResponse(
            success=False,
            message=str(e),
            object=None,
            errors=[str(e)]
        ) 