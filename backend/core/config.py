"""
CuraGenie Configuration Management System

This module provides environment-specific configuration management with secure secrets handling,
validation, and automatic environment detection.
"""

import os
import secrets
from typing import List, Optional, Dict, Any
from pydantic import BaseSettings, validator, Field
from pydantic_settings import BaseSettings
import logging

logger = logging.getLogger(__name__)

class ConfigurationError(Exception):
    """Configuration error exception"""
    pass

class BaseConfig:
    """Base configuration with common settings"""
    
    # Application
    APP_NAME: str = "CuraGenie"
    API_VERSION: str = "v1"
    API_PREFIX: str = "/api"
    
    # Environment
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE_PATH: str = Field(default="logs/curagenie.log", env="LOG_FILE_PATH")
    ERROR_LOG_PATH: str = Field(default="logs/errors.log", env="ERROR_LOG_PATH")
    REQUEST_LOG_PATH: str = Field(default="logs/requests.log", env="REQUEST_LOG_PATH")
    OPERATION_LOG_PATH: str = Field(default="logs/operations.log", env="OPERATION_LOG_PATH")
    LOG_RETENTION_DAYS: int = Field(default=30, env="LOG_RETENTION_DAYS")
    
    # Error Handling
    ENABLE_REQUEST_LOGGING: bool = Field(default=True, env="ENABLE_REQUEST_LOGGING")
    ENABLE_OPERATION_LOGGING: bool = Field(default=True, env="ENABLE_OPERATION_LOGGING")
    ENABLE_ERROR_TRACKING: bool = Field(default=True, env="ENABLE_ERROR_TRACKING")
    ERROR_ALERT_THRESHOLD: int = Field(default=10, env="ERROR_ALERT_THRESHOLD")

class DevelopmentConfig(BaseConfig):
    """Development environment configuration"""
    
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    
    # Database
    DATABASE_URL: str = Field(default="sqlite:///./curagenie_dev.db", env="DATABASE_URL")
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        env="CORS_ORIGINS"
    )
    
    # Security (Development defaults - NOT for production)
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production", env="SECRET_KEY")
    JWT_SECRET_KEY: str = Field(default="dev-jwt-secret-change-in-production", env="JWT_SECRET_KEY")
    
    # External Services (Development)
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    AWS_ACCESS_KEY_ID: str = Field(default="", env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = Field(default="", env="AWS_SECRET_ACCESS_KEY")
    
    # Features
    ENABLE_GENOMIC_ANALYSIS: bool = True
    ENABLE_MRI_ANALYSIS: bool = True
    ENABLE_AI_CHATBOT: bool = True
    MAX_FILE_SIZE_MB: int = 100

class StagingConfig(BaseConfig):
    """Staging environment configuration"""
    
    DEBUG: bool = False
    LOG_LEVEL: str = "DEBUG"
    
    # Database
    DATABASE_URL: str = Field(env="DATABASE_URL")  # Required
    REDIS_URL: str = Field(env="REDIS_URL")  # Required
    
    # CORS
    CORS_ORIGINS: List[str] = Field(env="CORS_ORIGINS")  # Required
    
    # Security
    SECRET_KEY: str = Field(env="SECRET_KEY")  # Required
    JWT_SECRET_KEY: str = Field(env="JWT_SECRET_KEY")  # Required
    
    # External Services
    OPENAI_API_KEY: str = Field(env="OPENAI_API_KEY")
    AWS_ACCESS_KEY_ID: str = Field(env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = Field(env="AWS_SECRET_ACCESS_KEY")
    
    # Features
    ENABLE_GENOMIC_ANALYSIS: bool = True
    ENABLE_MRI_ANALYSIS: bool = True
    ENABLE_AI_CHATBOT: bool = True
    MAX_FILE_SIZE_MB: int = 100

class ProductionConfig(BaseConfig):
    """Production environment configuration"""
    
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    FORCE_HTTPS: bool = True
    
    # Database
    DATABASE_URL: str = Field(env="DATABASE_URL")  # Required
    REDIS_URL: str = Field(env="REDIS_URL")  # Required
    
    # CORS
    CORS_ORIGINS: List[str] = Field(env="CORS_ORIGINS")  # Required
    
    # Security
    SECRET_KEY: str = Field(env="SECRET_KEY")  # Required
    JWT_SECRET_KEY: str = Field(env="JWT_SECRET_KEY")  # Required
    
    # External Services
    OPENAI_API_KEY: str = Field(env="OPENAI_API_KEY")
    AWS_ACCESS_KEY_ID: str = Field(env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = Field(env="AWS_SECRET_ACCESS_KEY")
    
    # Features
    ENABLE_GENOMIC_ANALYSIS: bool = Field(default=True, env="ENABLE_GENOMIC_ANALYSIS")
    ENABLE_MRI_ANALYSIS: bool = Field(default=True, env="ENABLE_MRI_ANALYSIS")
    ENABLE_AI_CHATBOT: bool = Field(default=True, env="ENABLE_AI_CHATBOT")
    MAX_FILE_SIZE_MB: int = Field(default=100, env="MAX_FILE_SIZE_MB")

class SecretsManager:
    """Secure secrets management system"""
    
    def __init__(self, environment: str):
        self.environment = environment
        self._secrets: Dict[str, str] = {}
        self._load_secrets()
    
    def _load_secrets(self):
        """Load secrets based on environment"""
        if self.environment == "production":
            self._load_production_secrets()
        elif self.environment == "staging":
            self._load_staging_secrets()
        else:
            self._load_development_secrets()
    
    def _load_production_secrets(self):
        """Load production secrets from secure sources"""
        # In production, integrate with AWS Secrets Manager, Azure Key Vault, etc.
        # For now, use environment variables
        required_secrets = [
            "SECRET_KEY", "JWT_SECRET_KEY", "DATABASE_URL", "REDIS_URL"
        ]
        
        for secret in required_secrets:
            value = os.getenv(secret)
            if not value:
                raise ConfigurationError(f"Required production secret {secret} not found")
            self._secrets[secret] = value
    
    def _load_staging_secrets(self):
        """Load staging secrets"""
        required_secrets = [
            "SECRET_KEY", "JWT_SECRET_KEY", "DATABASE_URL", "REDIS_URL"
        ]
        
        for secret in required_secrets:
            value = os.getenv(secret)
            if not value:
                raise ConfigurationError(f"Required staging secret {secret} not found")
            self._secrets[secret] = value
    
    def _load_development_secrets(self):
        """Load development secrets (with defaults)"""
        # Development can use defaults for non-critical secrets
        self._secrets = {
            "SECRET_KEY": os.getenv("SECRET_KEY", "dev-secret-key-change-in-production"),
            "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-change-in-production"),
            "DATABASE_URL": os.getenv("DATABASE_URL", "sqlite:///./curagenie_dev.db"),
            "REDIS_URL": os.getenv("REDIS_URL", "redis://localhost:6379/0")
        }
    
    def get_secret(self, key: str, required: bool = True) -> Optional[str]:
        """Get a secret value"""
        value = self._secrets.get(key) or os.getenv(key)
        
        if not value and required:
            raise ConfigurationError(f"Required secret {key} not found")
        
        return value
    
    def validate_secrets(self) -> bool:
        """Validate all required secrets are available"""
        try:
            if self.environment in ["production", "staging"]:
                required = ["SECRET_KEY", "JWT_SECRET_KEY", "DATABASE_URL", "REDIS_URL"]
            else:
                required = ["DATABASE_URL"]
            
            for secret in required:
                if not self.get_secret(secret, required=False):
                    logger.warning(f"Secret {secret} not found for {self.environment} environment")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Secret validation failed: {e}")
            return False

class ConfigurationManager:
    """Main configuration manager"""
    
    def __init__(self):
        self.environment = self._detect_environment()
        self.secrets_manager = SecretsManager(self.environment)
        self.config = self._load_config()
        self._validate_config()
    
    def _detect_environment(self) -> str:
        """Automatically detect environment"""
        env = os.getenv("ENVIRONMENT", "").lower()
        
        if env in ["production", "prod"]:
            return "production"
        elif env in ["staging", "stage"]:
            return "staging"
        else:
            return "development"
    
    def _load_config(self) -> BaseConfig:
        """Load environment-specific configuration"""
        if self.environment == "production":
            return ProductionConfig()
        elif self.environment == "staging":
            return StagingConfig()
        else:
            return DevelopmentConfig()
    
    def _validate_config(self):
        """Validate configuration on startup"""
        logger.info(f"🔍 Validating configuration for {self.environment} environment...")
        
        # Validate secrets
        if not self.secrets_manager.validate_secrets():
            logger.warning("⚠️ Some secrets are missing or invalid")
        
        # Validate required environment variables
        self._validate_environment_variables()
        
        # Validate CORS configuration
        self._validate_cors_config()
        
        logger.info("✅ Configuration validation completed")
    
    def _validate_environment_variables(self):
        """Validate required environment variables"""
        required_vars = []
        
        if self.environment in ["production", "staging"]:
            required_vars.extend([
                "DATABASE_URL", "REDIS_URL", "CORS_ORIGINS"
            ])
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.warning(f"⚠️ Missing environment variables: {', '.join(missing_vars)}")
    
    def _validate_cors_config(self):
        """Validate CORS configuration"""
        if self.environment == "production":
            cors_origins = self.get("CORS_ORIGINS", [])
            if "*" in cors_origins:
                logger.warning("⚠️ Wildcard CORS origin (*) detected in production - security risk!")
            
            if not any(origin.startswith("https://") for origin in cors_origins):
                logger.warning("⚠️ No HTTPS CORS origins detected in production")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return getattr(self.config, key, default)
    
    def get_secret(self, key: str, required: bool = True) -> Optional[str]:
        """Get secret value"""
        return self.secrets_manager.get_secret(key, required)
    
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == "production"
    
    def is_staging(self) -> bool:
        """Check if running in staging"""
        return self.environment == "staging"
    
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == "development"
    
    def get_cors_origins(self) -> List[str]:
        """Get CORS origins as list"""
        origins = self.get("CORS_ORIGINS", [])
        if isinstance(origins, str):
            return [origin.strip() for origin in origins.split(",")]
        return origins
    
    def get_database_url(self) -> str:
        """Get database URL with fallback"""
        return self.get_secret("DATABASE_URL") or self.get("DATABASE_URL")
    
    def get_redis_url(self) -> str:
        """Get Redis URL with fallback"""
        return self.get_secret("REDIS_URL") or self.get("REDIS_URL")
    
    def print_config_summary(self):
        """Print configuration summary for debugging"""
        logger.info("=" * 60)
        logger.info("🔧 CuraGenie Configuration Summary")
        logger.info("=" * 60)
        logger.info(f"Environment: {self.environment}")
        logger.info(f"Debug Mode: {self.get('DEBUG')}")
        logger.info(f"Log Level: {self.get('LOG_LEVEL')}")
        logger.info(f"Database: {self.get_database_url()[:30]}...")
        logger.info(f"CORS Origins: {len(self.get_cors_origins())} configured")
        logger.info(f"Features: Genomic={self.get('ENABLE_GENOMIC_ANALYSIS')}, "
                   f"MRI={self.get('ENABLE_MRI_ANALYSIS')}, "
                   f"Chatbot={self.get('ENABLE_AI_CHATBOT')}")
        logger.info("=" * 60)

# Global configuration instance
config_manager = ConfigurationManager()

# Legacy compatibility - maintain existing interface
class Settings(BaseSettings):
    """Legacy settings class for backward compatibility"""
    
    # Database
    database_url: str = config_manager.get_database_url()
    
    # Redis
    redis_url: str = config_manager.get_redis_url()
    
    # AWS
    aws_access_key_id: str = config_manager.get_secret("AWS_ACCESS_KEY_ID", required=False) or ""
    aws_secret_access_key: str = config_manager.get_secret("AWS_SECRET_ACCESS_KEY", required=False) or ""
    s3_bucket_name: str = "curagenie-genomic-data"
    aws_region: str = "us-east-1"
    
    # Application
    secret_key: str = config_manager.get_secret("SECRET_KEY")
    debug: bool = config_manager.get("DEBUG")
    cors_origins: str = ",".join(config_manager.get_cors_origins())
    
    # Celery
    celery_broker_url: str = config_manager.get_redis_url()
    celery_result_backend: str = config_manager.get_redis_url()
    
    # LLM Configuration
    openai_api_key: str = config_manager.get_secret("OPENAI_API_KEY", required=False) or ""
    anthropic_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    llm_provider: str = "openai"
    llm_model: str = "gpt-3.5-turbo"
    
    # Error Handling and Logging
    log_level: str = config_manager.get("LOG_LEVEL")
    log_file_path: str = config_manager.get("LOG_FILE_PATH")
    error_log_path: str = config_manager.get("ERROR_LOG_PATH")
    request_log_path: str = config_manager.get("REQUEST_LOG_PATH")
    operation_log_path: str = config_manager.get("OPERATION_LOG_PATH")
    enable_request_logging: bool = config_manager.get("ENABLE_REQUEST_LOGGING")
    enable_operation_logging: bool = config_manager.get("ENABLE_OPERATION_LOGGING")
    log_retention_days: int = config_manager.get("LOG_RETENTION_DAYS")
    enable_error_tracking: bool = config_manager.get("ENABLE_ERROR_TRACKING")
    error_alert_threshold: int = config_manager.get("ERROR_ALERT_THRESHOLD")
    
    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from string to list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"

# Create settings instance
settings = Settings()

# Print configuration summary on import
if __name__ != "__main__":
    config_manager.print_config_summary()
