from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    # PostgreSQL (for production): "postgresql://postgres:password@localhost:5432/curagenie"
    # SQLite (for development):
    database_url: str = "sqlite:///./curagenie.db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # AWS
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    s3_bucket_name: str = "curagenie-genomic-data"
    aws_region: str = "us-east-1"
    
    # Application
    secret_key: str = "your-super-secret-key-here"
    debug: bool = True
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000,https://cura-g.vercel.app"
    
    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    # LLM Configuration
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    llm_provider: str = "openai"  # options: "openai", "anthropic", "ollama"
    llm_model: str = "gpt-3.5-turbo"  # model to use
    
    # Error Handling and Logging
    log_level: str = "INFO"
    log_file_path: str = "logs/curagenie.log"
    error_log_path: str = "logs/errors.log"
    request_log_path: str = "logs/requests.log"
    operation_log_path: str = "logs/operations.log"
    enable_request_logging: bool = True
    enable_operation_logging: bool = True
    log_retention_days: int = 30
    enable_error_tracking: bool = True
    error_alert_threshold: int = 10  # Alert after 10 errors in 1 minute
    
    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from string to list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"

settings = Settings()
