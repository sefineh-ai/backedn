"""
Security utilities for password hashing and verification.
"""
from datetime import datetime, timedelta
from typing import Any, Union

from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to check against
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Get password hash (alias for hash_password for consistency).
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return hash_password(password)


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time
        
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Union[dict, None]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token data if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None 


def create_verification_token(user_id: str) -> str:
    """
    Create a time-limited email verification token.
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.verification_token_expire_minutes)
    to_encode = {"sub": user_id, "scope": "email_verification", "exp": expire}
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def verify_verification_token(token: str) -> Union[str, None]:
    """
    Validate verification token and return user_id if valid.
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        if payload.get("scope") != "email_verification":
            return None
        return payload.get("sub")
    except JWTError:
        return None


def decode_verification_token(token: str) -> tuple[str | None, str | None]:
    """
    Decode verification token and classify status.
    Returns (user_id, status) where status in {"ok", "expired"} or (None, None) if invalid.
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        if payload.get("scope") != "email_verification":
            return None, None
        return payload.get("sub"), "ok"
    except ExpiredSignatureError:
        # Re-decode without exp check but still verify signature by passing options
        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[ALGORITHM],
                options={"verify_exp": False},
            )
            if payload.get("scope") != "email_verification":
                return None, None
            return payload.get("sub"), "expired"
        except JWTError:
            return None, None
    except JWTError:
        return None, None