"""
Configuration management using Pydantic settings.
"""
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = Field(default="Enterprise Backend", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    
    # Database
    database_url: str = Field(default="sqlite:///./enterprise_backend.db", description="Database connection URL")
    database_echo: bool = Field(default=False, description="Database echo mode")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379", description="Redis connection URL")
    
    # Security
    secret_key: str = Field(default="your-secret-key-here-change-in-production", description="Secret key for JWT")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiration")
    refresh_token_expire_days: int = Field(default=7, description="Refresh token expiration")
    verification_token_expire_minutes: int = Field(default=60, description="Email verification token expiration in minutes")
    public_base_url: str = Field(default="http://localhost:8000", description="Public base URL for building links in emails")
    
    # Email (SMTP)
    smtp_host: Optional[str] = Field(default=None, description="SMTP server host")
    smtp_port: Optional[int] = Field(default=None, description="SMTP server port")
    smtp_user: Optional[str] = Field(default=None, description="SMTP username")
    smtp_password: Optional[str] = Field(default=None, description="SMTP password")
    smtp_use_tls: bool = Field(default=True, description="Use TLS for SMTP")
    from_email: str = Field(default="no-reply@example.com", description="From email address for outgoing emails")
    
    # CORS
    allowed_origins: list[str] = Field(default=["*"], description="Allowed CORS origins")
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, description="Rate limit per minute")
    
    # Logging
    log_level: str = Field(default="INFO", description="Log level")
    
    # External Services
    sentry_dsn: Optional[str] = Field(default=None, description="Sentry DSN")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings() 