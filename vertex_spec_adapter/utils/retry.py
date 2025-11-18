"""Retry logic with exponential backoff and circuit breaker for Vertex Spec Adapter."""

import time
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from threading import Lock
from typing import Callable, Dict, Optional, TypeVar

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from vertex_spec_adapter.core.exceptions import (
    APIError,
    QuotaExceededError,
    RateLimitError,
)
from vertex_spec_adapter.utils.logging import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


class CircuitState(str, Enum):
    """Circuit breaker states."""
    
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.
    
    Prevents cascading failures by opening the circuit after repeated failures
    and allowing it to recover gradually.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception,
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exception: Exception type that triggers circuit breaker
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.success_count = 0
        self._lock = Lock()
        
        logger.info(
            "CircuitBreaker initialized",
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
        )
    
    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
        
        Returns:
            Function result
        
        Raises:
            CircuitBreakerOpenError: If circuit is open
            Exception: If function raises exception
        """
        with self._lock:
            # Check if circuit should transition
            if self.state == CircuitState.OPEN:
                if self._should_attempt_recovery():
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                    logger.info("Circuit breaker entering HALF_OPEN state")
                else:
                    raise APIError(
                        "Circuit breaker is OPEN. Service is unavailable.",
                        status_code=503,
                        retryable=True,
                        suggested_fix=f"Wait {self.recovery_timeout} seconds and retry",
                    )
        
        # Execute function
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_recovery(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        if self.last_failure_time is None:
            return True
        
        elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout
    
    def _on_success(self) -> None:
        """Handle successful call."""
        with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= 1:  # Single success closes circuit
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    logger.info("Circuit breaker CLOSED after successful recovery")
            elif self.state == CircuitState.CLOSED:
                # Reset failure count on success
                self.failure_count = 0
    
    def _on_failure(self) -> None:
        """Handle failed call."""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()
            
            if self.state == CircuitState.HALF_OPEN:
                # Any failure in half-open opens circuit
                self.state = CircuitState.OPEN
                logger.warning("Circuit breaker OPENED after failure in HALF_OPEN state")
            elif self.state == CircuitState.CLOSED:
                if self.failure_count >= self.failure_threshold:
                    self.state = CircuitState.OPEN
                    logger.warning(
                        "Circuit breaker OPENED",
                        failure_count=self.failure_count,
                        threshold=self.failure_threshold,
                    )
    
    def reset(self) -> None:
        """Manually reset circuit breaker to CLOSED state."""
        with self._lock:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = None
            logger.info("Circuit breaker manually reset")


def retry_with_backoff(
    max_retries: int = 3,
    initial_wait: float = 1.0,
    max_wait: float = 60.0,
    exponential_base: float = 2.0,
    retryable_errors: tuple = (RateLimitError, QuotaExceededError, APIError),
):
    """
    Decorator for retrying functions with exponential backoff.
    
    Retries transient errors (429, 500, 502, 503, 504) with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_wait: Initial wait time in seconds
        max_wait: Maximum wait time in seconds
        exponential_base: Base for exponential backoff
        retryable_errors: Tuple of exception types that should be retried
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        @retry(
            stop=stop_after_attempt(max_retries + 1),
            wait=wait_exponential(
                multiplier=initial_wait,
                max=max_wait,
                exp_base=exponential_base
            ),
            retry=retry_if_exception_type(retryable_errors),
            reraise=True,
        )
        def wrapper(*args, **kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except retryable_errors as e:
                # Check if error has retry_after
                if hasattr(e, 'retry_after') and e.retry_after:
                    time.sleep(e.retry_after)
                raise
        
        return wrapper
    return decorator


def retry_on_transient_errors(
    max_retries: int = 3,
    initial_wait: float = 1.0,
    max_wait: float = 60.0,
):
    """
    Retry decorator specifically for transient HTTP errors (429, 500, 502, 503, 504).
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_wait: Initial wait time in seconds
        max_wait: Maximum wait time in seconds
    """
    def should_retry(exception: Exception) -> bool:
        """Check if exception is a transient error."""
        if isinstance(exception, (RateLimitError, QuotaExceededError)):
            return True
        if isinstance(exception, APIError):
            # Retry on 429, 500, 502, 503, 504
            if exception.status_code in (429, 500, 502, 503, 504):
                return exception.retryable
        return False
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        @retry(
            stop=stop_after_attempt(max_retries + 1),
            wait=wait_exponential(
                multiplier=initial_wait,
                max=max_wait,
            ),
            retry=retry_if_exception_type((APIError, RateLimitError, QuotaExceededError)),
            reraise=True,
        )
        def wrapper(*args, **kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if should_retry(e):
                    # Check if error has retry_after
                    if hasattr(e, 'retry_after') and e.retry_after:
                        time.sleep(e.retry_after)
                    raise
                raise
        
        return wrapper
    return decorator

