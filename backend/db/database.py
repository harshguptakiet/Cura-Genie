from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from core.config import settings
import logging
import os

logger = logging.getLogger(__name__)

def get_database_url() -> str:
    """Get database URL from environment or fallback to default"""
    # Check if DATABASE_URL environment variable is set
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        logger.info("Using DATABASE_URL from environment")
        return database_url
    
    # Fallback to settings (which should be set in .env)
    if settings.database_url and settings.database_url != "postgresql://":
        logger.info("Using database URL from settings")
        return settings.database_url
    
    # Final fallback for development
    logger.warning("No DATABASE_URL found, using SQLite fallback")
    return "sqlite:///./curagenie.db"

def create_database_engine():
    """Create database engine with appropriate configuration"""
    database_url = get_database_url()
    
    # PostgreSQL-specific configurations
    if database_url.startswith('postgresql://'):
        logger.info("Configuring PostgreSQL database connection")
        return create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=10,
            max_overflow=20,
            echo=settings.debug,  # Log SQL queries in debug mode
            # PostgreSQL-specific options
            connect_args={
                "connect_timeout": 10,
                "application_name": "CuraGenie"
            }
        )
    else:
        # SQLite configuration
        logger.info("Configuring SQLite database connection")
        return create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=settings.debug,  # Log SQL queries in debug mode
            # SQLite-specific options
            connect_args={"check_same_thread": False}
        )

# Create SQLAlchemy engine
engine = create_database_engine()

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

def get_db() -> Session:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    try:
        # Import all models to ensure they're registered with Base
        from db.models import GenomicData, PrsScore, MlPrediction
        from db.auth_models import User, PatientProfile, MedicalReport
        
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Log database type
        database_url = get_database_url()
        if database_url.startswith('postgresql://'):
            logger.info("✅ Using PostgreSQL database")
        else:
            logger.info("✅ Using SQLite database")
            
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise

def test_database_connection():
    """Test database connection"""
    try:
        with engine.connect() as connection:
            if get_database_url().startswith('postgresql://'):
                result = connection.execute("SELECT version()")
                version = result.fetchone()[0]
                logger.info(f"✅ PostgreSQL connection successful. Version: {version}")
            else:
                result = connection.execute("SELECT sqlite_version()")
                version = result.fetchone()[0]
                logger.info(f"✅ SQLite connection successful. Version: {version}")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False
