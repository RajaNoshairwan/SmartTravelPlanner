"""
Logging utility for the Travel AI system.
"""
import logging
import logging.config
from typing import Optional
from pathlib import Path
import sys
from functools import wraps
import time
import traceback

from config import LOGGING_CONFIG

# Configure logging
logging.config.dictConfig(LOGGING_CONFIG)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    return logging.getLogger(name)

def log_error(logger: logging.Logger, error: Exception, context: Optional[dict] = None):
    """Log an error with optional context information."""
    error_info = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": traceback.format_exc(),
    }
    if context:
        error_info.update(context)
    
    logger.error("Error occurred", extra=error_info)

def log_performance(logger: logging.Logger, operation: str, duration: float, 
                   context: Optional[dict] = None):
    """Log performance metrics for an operation."""
    perf_info = {
        "operation": operation,
        "duration_ms": round(duration * 1000, 2),
    }
    if context:
        perf_info.update(context)
    
    logger.info("Performance metric", extra=perf_info)

def log_api_call(logger: logging.Logger, api_name: str, endpoint: str, 
                status_code: int, duration: float, context: Optional[dict] = None):
    """Log API call details."""
    api_info = {
        "api": api_name,
        "endpoint": endpoint,
        "status_code": status_code,
        "duration_ms": round(duration * 1000, 2),
    }
    if context:
        api_info.update(context)
    
    logger.info("API call", extra=api_info)

def performance_logger(operation_name: Optional[str] = None):
    """Decorator to log performance metrics for a function."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            op_name = operation_name or func.__name__
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                log_performance(logger, op_name, duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                log_error(logger, e, {
                    "operation": op_name,
                    "duration_ms": round(duration * 1000, 2)
                })
                raise
        return wrapper
    return decorator

def api_logger(api_name: str):
    """Decorator to log API calls."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            endpoint = func.__name__
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Assuming the result has a status_code attribute
                status_code = getattr(result, 'status_code', 200)
                
                log_api_call(logger, api_name, endpoint, status_code, duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                log_error(logger, e, {
                    "api": api_name,
                    "endpoint": endpoint,
                    "duration_ms": round(duration * 1000, 2)
                })
                raise
        return wrapper
    return decorator

class LoggerContext:
    """Context manager for logging operations."""
    def __init__(self, logger: logging.Logger, operation: str):
        self.logger = logger
        self.operation = operation
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        self.logger.info(f"Starting operation: {self.operation}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        if exc_type is None:
            log_performance(self.logger, self.operation, duration)
        else:
            log_error(self.logger, exc_val, {
                "operation": self.operation,
                "duration_ms": round(duration * 1000, 2)
            })
        return False  # Don't suppress exceptions 