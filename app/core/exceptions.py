"""
Custom exceptions for the application.
"""
from typing import Any, Dict, Optional


class BaseException(Exception):
    """Base exception class for the application."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class ValidationError(BaseException):
    """Validation error exception."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, status_code=400, details=details)


class AuthenticationError(BaseException):
    """Authentication error exception."""
    
    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message, status_code=401)


class AuthorizationError(BaseException):
    """Authorization error exception."""
    
    def __init__(self, message: str = "Insufficient permissions") -> None:
        super().__init__(message, status_code=403)


class NotFoundError(BaseException):
    """Not found error exception."""
    
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, status_code=404)


class ConflictError(BaseException):
    """Conflict error exception."""
    
    def __init__(self, message: str = "Resource conflict") -> None:
        super().__init__(message, status_code=409)


class BusinessLogicError(BaseException):
    """Business logic error exception."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, status_code=422, details=details) 