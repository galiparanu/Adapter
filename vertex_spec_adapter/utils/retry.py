"""Retry logic with exponential backoff for Vertex Spec Adapter."""

from typing import Callable, TypeVar, Optional
from functools import wraps
import time

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryError,
)

from vertex_spec_adapter.core.exceptions import (
    APIError,
    RateLimitError,
    QuotaExceededError,
)

T = TypeVar('T')


def retry_with_backoff(
    max_retries: int = 3,
    initial_wait: float = 1.0,
    max_wait: float = 60.0,
    exponential_base: float = 2.0,
    retryable_errors: tuple = (RateLimitError, QuotaExceededError, APIError)
):
    """
    Decorator for retrying functions with exponential backoff.
    
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

