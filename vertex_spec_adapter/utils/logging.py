"""Logging configuration and utilities."""

import logging
import re
from datetime import datetime
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
    log_file: Optional[str] = None,
    debug: bool = False,
) -> None:
    """
    Configure structured logging with structlog.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_format: Output format ('json' or 'text')
        log_file: Optional path to log file (stdout if None)
        debug: Enable debug mode with detailed diagnostics
    """
    # Override log level if debug mode
    if debug:
        log_level = "DEBUG"
    
    # Convert string level to logging constant
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure processors based on format
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    # Add debug-specific processors
    if debug:
        processors.insert(1, structlog.processors.add_logger_name)
        processors.insert(2, structlog.processors.CallsiteParameterAdder(
            parameters=[
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.LINENO,
                structlog.processors.CallsiteParameter.FUNC_NAME,
            ]
        ))
    
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
    
    if debug:
        logger = get_logger(__name__)
        logger.debug("Debug mode enabled with detailed diagnostics")


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


def log_api_call(
    model: str,
    input_tokens: int,
    output_tokens: int,
    latency_ms: Optional[float] = None,
    success: bool = True,
    error: Optional[str] = None,
    **kwargs
) -> None:
    """
    Log API call details for audit and monitoring.
    
    Args:
        model: Model identifier used
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        latency_ms: Optional request latency in milliseconds
        success: Whether the call was successful
        error: Optional error message
        **kwargs: Additional context to log
    """
    logger = get_logger(__name__)
    
    log_data = {
        "event_type": "api_call",
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "success": success,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    if latency_ms is not None:
        log_data["latency_ms"] = latency_ms
    
    if error:
        log_data["error"] = sanitize_error_message(Exception(error))
    
    # Add any additional context
    log_data.update(kwargs)
    
    # Sanitize log data
    log_data = sanitize_log_data(log_data)
    
    if success:
        logger.info("API call completed", **log_data)
    else:
        logger.error("API call failed", **log_data)


def log_audit_event(
    event_type: str,
    user: Optional[str] = None,
    action: Optional[str] = None,
    resource: Optional[str] = None,
    success: bool = True,
    error: Optional[str] = None,
    **kwargs
) -> None:
    """
    Log audit event for enterprise compliance.
    
    This creates structured audit logs suitable for compliance and security monitoring.
    
    Args:
        event_type: Type of event (e.g., 'authentication', 'api_call', 'config_change')
        user: Optional user identifier
        action: Optional action performed
        resource: Optional resource accessed
        success: Whether the action was successful
        error: Optional error message
        **kwargs: Additional audit fields
    """
    logger = get_logger(__name__)
    
    audit_data = {
        "event_type": "audit",
        "audit_event_type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "success": success,
    }
    
    if user:
        audit_data["user"] = user
    
    if action:
        audit_data["action"] = action
    
    if resource:
        audit_data["resource"] = resource
    
    if error:
        audit_data["error"] = sanitize_error_message(Exception(error))
    
    # Add any additional audit fields
    audit_data.update(kwargs)
    
    # Sanitize audit data
    audit_data = sanitize_log_data(audit_data)
    
    # Always log audit events at INFO level for compliance
    logger.info("Audit event", **audit_data)

