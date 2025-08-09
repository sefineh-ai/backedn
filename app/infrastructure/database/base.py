"""
Base database configuration using SQLAlchemy.
"""
from typing import Any, Dict

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings

# Create SQLAlchemy engine
# Use StaticPool and SQLite-specific connect args only for SQLite connections
database_url = settings.database_url
engine_kwargs: Dict[str, Any] = {
    "echo": settings.database_echo,
}

if database_url.startswith("sqlite"):
    # SQLite needs this flag when using the same DB in multiple threads
    engine_kwargs["connect_args"] = {"check_same_thread": False}
    # Use StaticPool primarily for tests / single-process SQLite usage
    engine_kwargs["poolclass"] = StaticPool

engine = create_engine(database_url, **engine_kwargs)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()


def get_db() -> Any:
    """
    Dependency to get database session.
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DatabaseManager:
    """
    Database manager for handling database operations.
    
    This class implements the Singleton pattern for database management.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.engine = engine
            self.SessionLocal = SessionLocal
            self.Base = Base
            self.initialized = True
    
    def create_tables(self) -> None:
        """Create all tables."""
        # Import all models to ensure they are registered
        from app.infrastructure.database.models import user, job, application
        self.Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self) -> None:
        """Drop all tables."""
        self.Base.metadata.drop_all(bind=self.engine)
    
    def get_session(self):
        """Get a new database session."""
        return self.SessionLocal() 