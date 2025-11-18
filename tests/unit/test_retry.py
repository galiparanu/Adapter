"""Unit tests for retry logic and circuit breaker."""

import time
from unittest.mock import Mock, patch

import pytest

from vertex_spec_adapter.core.exceptions import APIError, RateLimitError
from vertex_spec_adapter.utils.retry import (
    CircuitBreaker,
    CircuitState,
    retry_on_transient_errors,
    retry_with_backoff,
)


class TestRetryWithBackoff:
    """Tests for retry_with_backoff decorator."""
    
    def test_successful_call_no_retry(self):
        """Test that successful calls don't retry."""
        @retry_with_backoff(max_retries=3)
        def successful_func():
            return "success"
        
        assert successful_func() == "success"
    
    def test_retry_on_rate_limit_error(self):
        """Test retry on RateLimitError."""
        call_count = [0]
        
        @retry_with_backoff(max_retries=3, initial_wait=0.1)
        def failing_func():
            call_count[0] += 1
            if call_count[0] < 2:
                raise RateLimitError("Rate limit exceeded", retry_after=0.1)
            return "success"
        
        result = failing_func()
        assert result == "success"
        assert call_count[0] == 2
    
    def test_max_retries_exceeded(self):
        """Test that max retries are respected."""
        call_count = [0]
        
        @retry_with_backoff(max_retries=2, initial_wait=0.01)
        def always_failing_func():
            call_count[0] += 1
            raise RateLimitError("Rate limit exceeded")
        
        with pytest.raises(RateLimitError):
            always_failing_func()
        
        assert call_count[0] == 3  # Initial + 2 retries
    
    def test_non_retryable_error_not_retried(self):
        """Test that non-retryable errors are not retried."""
        call_count = [0]
        
        @retry_with_backoff(max_retries=3)
        def non_retryable_error_func():
            call_count[0] += 1
            raise ValueError("Not retryable")
        
        with pytest.raises(ValueError):
            non_retryable_error_func()
        
        assert call_count[0] == 1


class TestRetryOnTransientErrors:
    """Tests for retry_on_transient_errors decorator."""
    
    def test_retry_on_500_error(self):
        """Test retry on 500 error."""
        call_count = [0]
        
        @retry_on_transient_errors(max_retries=3, initial_wait=0.1)
        def failing_func():
            call_count[0] += 1
            if call_count[0] < 2:
                raise APIError("Server error", status_code=500, retryable=True)
            return "success"
        
        result = failing_func()
        assert result == "success"
        assert call_count[0] == 2
    
    def test_retry_on_429_error(self):
        """Test retry on 429 error."""
        call_count = [0]
        
        @retry_on_transient_errors(max_retries=3, initial_wait=0.1)
        def failing_func():
            call_count[0] += 1
            if call_count[0] < 2:
                raise APIError("Rate limit", status_code=429, retryable=True)
            return "success"
        
        result = failing_func()
        assert result == "success"
        assert call_count[0] == 2
    
    def test_no_retry_on_400_error(self):
        """Test that 400 errors are not retried."""
        call_count = [0]
        
        @retry_on_transient_errors(max_retries=3)
        def failing_func():
            call_count[0] += 1
            raise APIError("Bad request", status_code=400, retryable=False)
        
        with pytest.raises(APIError):
            failing_func()
        
        assert call_count[0] == 1


class TestCircuitBreaker:
    """Tests for CircuitBreaker class."""
    
    def test_initial_state_closed(self):
        """Test that circuit breaker starts in CLOSED state."""
        cb = CircuitBreaker()
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
    
    def test_successful_call_resets_failure_count(self):
        """Test that successful calls reset failure count."""
        cb = CircuitBreaker(failure_threshold=3)
        
        def successful_func():
            return "success"
        
        result = cb.call(successful_func)
        assert result == "success"
        assert cb.failure_count == 0
        assert cb.state == CircuitState.CLOSED
    
    def test_failure_increments_count(self):
        """Test that failures increment count."""
        cb = CircuitBreaker(failure_threshold=3)
        
        def failing_func():
            raise APIError("Error", status_code=500)
        
        with pytest.raises(APIError):
            cb.call(failing_func)
        
        assert cb.failure_count == 1
        assert cb.state == CircuitState.CLOSED
    
    def test_circuit_opens_after_threshold(self):
        """Test that circuit opens after failure threshold."""
        cb = CircuitBreaker(failure_threshold=2)
        
        def failing_func():
            raise APIError("Error", status_code=500)
        
        # First failure
        with pytest.raises(APIError):
            cb.call(failing_func)
        assert cb.state == CircuitState.CLOSED
        
        # Second failure - should open
        with pytest.raises(APIError):
            cb.call(failing_func)
        assert cb.state == CircuitState.OPEN
    
    def test_open_circuit_rejects_requests(self):
        """Test that open circuit rejects requests."""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=60)
        
        def failing_func():
            raise APIError("Error", status_code=500)
        
        # Open circuit
        with pytest.raises(APIError):
            cb.call(failing_func)
        
        assert cb.state == CircuitState.OPEN
        
        # Try to call again - should be rejected
        def any_func():
            return "should not execute"
        
        with pytest.raises(APIError) as exc_info:
            cb.call(any_func)
        
        assert "Circuit breaker is OPEN" in str(exc_info.value)
    
    def test_circuit_enters_half_open_after_timeout(self):
        """Test that circuit enters HALF_OPEN after recovery timeout."""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1)
        
        def failing_func():
            raise APIError("Error", status_code=500)
        
        # Open circuit
        with pytest.raises(APIError):
            cb.call(failing_func)
        
        assert cb.state == CircuitState.OPEN
        
        # Wait for recovery timeout
        time.sleep(0.15)
        
        # Next call should enter HALF_OPEN
        def successful_func():
            return "success"
        
        result = cb.call(successful_func)
        assert result == "success"
        assert cb.state == CircuitState.HALF_OPEN
    
    def test_half_open_success_closes_circuit(self):
        """Test that successful call in HALF_OPEN closes circuit."""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1)
        
        def failing_func():
            raise APIError("Error", status_code=500)
        
        # Open circuit
        with pytest.raises(APIError):
            cb.call(failing_func)
        
        # Wait for recovery
        time.sleep(0.15)
        
        # Successful call in HALF_OPEN
        def successful_func():
            return "success"
        
        result = cb.call(successful_func)
        assert result == "success"
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
    
    def test_half_open_failure_reopens_circuit(self):
        """Test that failure in HALF_OPEN reopens circuit."""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1)
        
        def failing_func():
            raise APIError("Error", status_code=500)
        
        # Open circuit
        with pytest.raises(APIError):
            cb.call(failing_func)
        
        # Wait for recovery
        time.sleep(0.15)
        
        # Failure in HALF_OPEN should reopen
        with pytest.raises(APIError):
            cb.call(failing_func)
        
        assert cb.state == CircuitState.OPEN
    
    def test_manual_reset(self):
        """Test manual reset of circuit breaker."""
        cb = CircuitBreaker(failure_threshold=1)
        
        def failing_func():
            raise APIError("Error", status_code=500)
        
        # Open circuit
        with pytest.raises(APIError):
            cb.call(failing_func)
        
        assert cb.state == CircuitState.OPEN
        
        # Reset
        cb.reset()
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
        assert cb.success_count == 0
        assert cb.last_failure_time is None
    
    def test_thread_safety(self):
        """Test that circuit breaker is thread-safe."""
        import threading
        
        cb = CircuitBreaker(failure_threshold=10)
        
        def failing_func():
            raise APIError("Error", status_code=500)
        
        def call_func():
            try:
                cb.call(failing_func)
            except APIError:
                pass
        
        # Call from multiple threads
        threads = [threading.Thread(target=call_func) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Should have accumulated failures
        assert cb.failure_count >= 10

