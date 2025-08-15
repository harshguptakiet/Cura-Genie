"""
Unified Database Manager for CuraGenie

This module provides a centralized database management system that:
- Standardizes database connections across all modules
- Implements proper connection pooling
- Provides consistent session management
- Handles database initialization and migrations
"""

import logging
from typing import Generator, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager

from core.config import config_manager

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Unified database manager for CuraGenie"""
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize database manager with connection pooling"""
        self.database_url = database_url or config_manager.get_database_url()
        self.engine = None
        self.SessionLocal = None
        self._scoped_session = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize SQLAlchemy engine with proper configuration"""
        try:
            # PostgreSQL-specific configurations
            if self.database_url.startswith('postgresql://'):
                logger.info("🔧 Initializing PostgreSQL engine with connection pooling")
                self.engine = create_engine(
                    self.database_url,
                    poolclass=QueuePool,
                    pool_size=10,
                    max_overflow=20,
                    pool_pre_ping=True,
                    pool_recycle=300,
                    pool_timeout=30,
                    echo=config_manager.get("DEBUG", False),
                    connect_args={
                        "connect_timeout": 10,
                        "application_name": "CuraGenie"
                    }
                )
            else:
                # SQLite configuration
                logger.info("🔧 Initializing SQLite engine")
                self.engine = create_engine(
                    self.database_url,
                    pool_pre_ping=True,
                    pool_recycle=300,
                    echo=config_manager.get("DEBUG", False),
                    connect_args={"check_same_thread": False}
                )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Create scoped session for thread safety
            self._scoped_session = scoped_session(self.SessionLocal)
            
            logger.info("✅ Database engine initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize database engine: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get a new database session"""
        if not self.SessionLocal:
            raise RuntimeError("Database not initialized")
        return self.SessionLocal()
    
    def get_scoped_session(self) -> Session:
        """Get a scoped database session (thread-safe)"""
        if not self._scoped_session:
            raise RuntimeError("Database not initialized")
        return self._scoped_session()
    
    @contextmanager
    def get_session_context(self) -> Generator[Session, None, None]:
        """Context manager for database sessions with automatic cleanup"""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.engine.connect() as connection:
                if self.database_url.startswith('postgresql://'):
                    result = connection.execute(text("SELECT version()"))
                    version = result.fetchone()[0]
                    logger.info(f"✅ PostgreSQL connection successful. Version: {version}")
                else:
                    result = connection.execute(text("SELECT sqlite_version()"))
                    version = result.fetchone()[0]
                    logger.info(f"✅ SQLite connection successful. Version: {version}")
                return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def get_connection_info(self) -> dict:
        """Get database connection information"""
        return {
            "database_url": self.database_url,
            "database_type": "postgresql" if self.database_url.startswith('postgresql://') else "sqlite",
            "pool_size": getattr(self.engine.pool, 'size', 'N/A'),
            "pool_overflow": getattr(self.engine.pool, 'overflow', 'N/A'),
            "pool_checked_in": getattr(self.engine.pool, 'checkedin', 'N/A'),
            "pool_checked_out": getattr(self.engine.pool, 'checkedout', 'N/A'),
        }
    
    def close_all_connections(self):
        """Close all database connections"""
        try:
            if self.engine:
                self.engine.dispose()
            logger.info("✅ All database connections closed")
        except Exception as e:
            logger.error(f"❌ Error closing database connections: {e}")
    
    def __del__(self):
        """Cleanup on deletion"""
        self.close_all_connections()

# Global database manager instance
db_manager = DatabaseManager()

# Dependency function for FastAPI
def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database sessions"""
    with db_manager.get_session_context() as session:
        yield session

# Dependency function for background tasks
def get_db_session() -> Session:
    """Get database session for background tasks"""
    return db_manager.get_session()

# Context manager for manual session management
def get_db_context():
    """Context manager for database sessions"""
    return db_manager.get_session_context()
