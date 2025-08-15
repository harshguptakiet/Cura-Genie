"""
Logging Configuration for CuraGenie Platform
Sets up structured logging with JSON format and file rotation
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Dict, Any

from .config import settings


def setup_logging():
    """Setup comprehensive logging configuration for the CuraGenie platform"""
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatters
    json_formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": %(message)s}'
    )
    
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handlers with rotation
    if not settings.debug:
        # Main application log
        main_handler = logging.handlers.RotatingFileHandler(
            settings.log_file_path,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        main_handler.setLevel(logging.INFO)
        main_handler.setFormatter(json_formatter)
        root_logger.addHandler(main_handler)
        
        # Error log
        error_handler = logging.handlers.RotatingFileHandler(
            settings.error_log_path,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(json_formatter)
        root_logger.addHandler(error_handler)
        
        # Request log
        if settings.enable_request_logging:
            request_handler = logging.handlers.RotatingFileHandler(
                settings.request_log_path,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            request_handler.setLevel(logging.INFO)
            request_handler.setFormatter(json_formatter)
            root_logger.addHandler(request_handler)
        
        # Operation log
        if settings.enable_operation_logging:
            operation_handler = logging.handlers.RotatingFileHandler(
                settings.operation_log_path,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            operation_handler.setLevel(logging.INFO)
            operation_handler.setFormatter(json_formatter)
            root_logger.addHandler(operation_handler)
    
    # Configure specific loggers
    configure_component_loggers()
    
    logging.info("Logging configuration completed successfully")


def configure_component_loggers():
    """Configure logging for specific components"""
    
    # API logger
    api_logger = logging.getLogger("curagenie_api")
    api_logger.setLevel(logging.INFO)
    
    # Database logger
    db_logger = logging.getLogger("curagenie_db")
    db_logger.setLevel(logging.INFO)
    
    # Genomic processing logger
    genomic_logger = logging.getLogger("curagenie_genomic")
    genomic_logger.setLevel(logging.INFO)
    
    # ML model logger
    ml_logger = logging.getLogger("curagenie_ml")
    ml_logger.setLevel(logging.INFO)
    
    # External service logger
    external_logger = logging.getLogger("curagenie_external")
    external_logger.setLevel(logging.INFO)
    
    # Authentication logger
    auth_logger = logging.getLogger("curagenie_auth")
    auth_logger.setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name"""
    return logging.getLogger(f"curagenie_{name}")


def log_structured(
    logger: logging.Logger,
    level: str,
    message: str,
    **kwargs
):
    """Log a structured message with additional context"""
    
    log_data = {
        "message": message,
        **kwargs
    }
    
    log_method = getattr(logger, level.lower(), logger.info)
    log_method(log_data)


def log_api_request(
    method: str,
    path: str,
    status_code: int,
    process_time: float,
    user_id: str = None,
    request_id: str = None,
    **kwargs
):
    """Log API request information"""
    
    logger = logging.getLogger("curagenie_api")
    
    log_data = {
        "type": "api_request",
        "method": method,
        "path": path,
        "status_code": status_code,
        "process_time": process_time,
        "user_id": user_id,
        "request_id": request_id,
        **kwargs
    }
    
    if status_code >= 400:
        logger.error(log_data)
    else:
        logger.info(log_data)


def log_database_operation(
    operation: str,
    table: str,
    success: bool,
    duration: float = None,
    **kwargs
):
    """Log database operation information"""
    
    logger = logging.getLogger("curagenie_db")
    
    log_data = {
        "type": "database_operation",
        "operation": operation,
        "table": table,
        "success": success,
        "duration": duration,
        **kwargs
    }
    
    if success:
        logger.info(log_data)
    else:
        logger.error(log_data)


def log_genomic_processing(
    operation: str,
    file_type: str,
    file_size: int,
    success: bool,
    duration: float = None,
    **kwargs
):
    """Log genomic processing information"""
    
    logger = logging.getLogger("curagenie_genomic")
    
    log_data = {
        "type": "genomic_processing",
        "operation": operation,
        "file_type": file_type,
        "file_size": file_size,
        "success": success,
        "duration": duration,
        **kwargs
    }
    
    if success:
        logger.info(log_data)
    else:
        logger.error(log_data)


def log_external_service_call(
    service: str,
    endpoint: str,
    success: bool,
    duration: float = None,
    status_code: int = None,
    **kwargs
):
    """Log external service call information"""
    
    logger = logging.getLogger("curagenie_external")
    
    log_data = {
        "type": "external_service_call",
        "service": service,
        "endpoint": endpoint,
        "success": success,
        "duration": duration,
        "status_code": status_code,
        **kwargs
    }
    
    if success:
        logger.info(log_data)
    else:
        logger.error(log_data)


def cleanup_old_logs():
    """Clean up old log files based on retention policy"""
    if not settings.log_retention_days:
        return
    
    logs_dir = Path("logs")
    if not logs_dir.exists():
        return
    
    import time
    current_time = time.time()
    cutoff_time = current_time - (settings.log_retention_days * 24 * 60 * 60)
    
    for log_file in logs_dir.glob("*.log*"):
        if log_file.stat().st_mtime < cutoff_time:
            try:
                log_file.unlink()
                logging.info(f"Removed old log file: {log_file}")
            except Exception as e:
                logging.warning(f"Failed to remove old log file {log_file}: {e}")
