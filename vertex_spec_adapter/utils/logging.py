"""Logging configuration and utilities."""

import logging
import re
from typing import Any, Dict, Optional

import structlog
from structlog.types import Processor


def sanitize_log_data(data: Any) -> Any:
    """
    Remove sensitive information from log data.
    
    Args:
        data: Data to sanitize (dict, list, or primitive)
    
    Returns:
        Sanitized data with sensitive values replaced
    """
    sensitive_keys = [
        'api_key',
        'token',
        'password',
        'secret',
        'credential',
        'authorization',
        'auth',
        'access_token',
        'refresh_token',
        'private_key',
        'service_account',
    ]
    
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            key_lower = key.lower()
            # Check if key contains sensitive terms
            if any(sensitive_term in key_lower for sensitive_term in sensitive_keys):
                sanitized[key] = '***REDACTED***'
            elif isinstance(value, (dict, list)):
                sanitized[key] = sanitize_log_data(value)
            elif isinstance(value, str) and len(value) > 50:
                # Check for potential base64 or JWT tokens
                if re.match(r'^[A-Za-z0-9+/]{20,}={0,2}$', value):
                    sanitized[key] = '***BASE64_DATA***'
                elif re.match(r'^eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$', value):
                    sanitized[key] = '***JWT***'
                else:
                    sanitized[key] = value
            else:
                sanitized[key] = value
        return sanitized
    elif isinstance(data, list):
        return [sanitize_log_data(item) for item in data]
    else:
        return data


def configure_logging(
    log_level: str = "INFO",
    log_format: str = "text",
    log_file: Optional[str] = None
) -> None:
    """
    Configure structured logging with structlog.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_format: Output format ('json' or 'text')
        log_file: Optional path to log file (stdout if None)
    """
    # Convert string level to logging constant
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure processors based on format
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    if log_format == "json":
        processors.extend([
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ])
    else:
        processors.extend([
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.dev.ConsoleRenderer(),
        ])
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: Optional[str] = None) -> structlog.BoundLogger:
    """
    Get a configured logger instance.
    
    Args:
        name: Optional logger name
    
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


def sanitize_error_message(error: Exception) -> str:
    """
    Remove potential secrets from error messages.
    
    Args:
        error: Exception to sanitize
    
    Returns:
        Sanitized error message string
    """
    message = str(error)
    
    # Remove base64-encoded data
    message = re.sub(
        r'[A-Za-z0-9+/]{20,}={0,2}',
        '***BASE64_DATA***',
        message
    )
    
    # Remove JSON Web Tokens
    message = re.sub(
        r'eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+',
        '***JWT***',
        message
    )
    
    # Remove potential API keys (long alphanumeric strings)
    message = re.sub(
        r'\b[A-Za-z0-9]{32,}\b',
        '***API_KEY***',
        message
    )
    
    return message

