"""Unit tests for UsageTracker."""

from datetime import datetime
from unittest.mock import patch

import pytest

from vertex_spec_adapter.utils.metrics import UsageTracker


class TestUsageTracker:
    """Test UsageTracker class."""
    
    def test_init_without_session_id(self):
        """Test UsageTracker initialization without session ID."""
        tracker = UsageTracker()
        
        assert tracker.session_id is not None
        assert tracker.metrics.total_requests == 0
        assert tracker.metrics.total_tokens == 0
        assert tracker.metrics.start_time is not None
    
    def test_init_with_session_id(self):
        """Test UsageTracker initialization with session ID."""
        tracker = UsageTracker(session_id="test-session-123")
        
        assert tracker.session_id == "test-session-123"
    
    def test_track_request(self):
        """Test tracking a single request."""
        tracker = UsageTracker()
        
        tracker.track_request(
            model="claude-4-5-sonnet",
            input_tokens=100,
            output_tokens=50,
            latency_ms=500.0,
        )
        
        assert tracker.metrics.total_requests == 1
        assert tracker.metrics.total_input_tokens == 100
        assert tracker.metrics.total_output_tokens == 50
        assert tracker.metrics.total_tokens == 150
        assert tracker.metrics.requests_by_model["claude-4-5-sonnet"] == 1
        assert tracker.metrics.estimated_cost_usd > 0
    
    def test_track_request_with_error(self):
        """Test tracking a request with error."""
        tracker = UsageTracker()
        error = Exception("API error")
        
        tracker.track_request(
            model="gemini-2-5-pro",
            input_tokens=200,
            output_tokens=0,
            error=error,
        )
        
        assert tracker.metrics.total_requests == 1
        assert len(tracker.metrics.errors) == 1
        assert tracker.metrics.errors[0]["model"] == "gemini-2-5-pro"
    
    def test_track_multiple_requests(self):
        """Test tracking multiple requests."""
        tracker = UsageTracker()
        
        tracker.track_request("claude-4-5-sonnet", 100, 50)
        tracker.track_request("gemini-2-5-pro", 200, 100)
        tracker.track_request("claude-4-5-sonnet", 150, 75)
        
        assert tracker.metrics.total_requests == 3
        assert tracker.metrics.total_input_tokens == 450
        assert tracker.metrics.total_output_tokens == 225
        assert tracker.metrics.total_tokens == 675
        assert tracker.metrics.requests_by_model["claude-4-5-sonnet"] == 2
        assert tracker.metrics.requests_by_model["gemini-2-5-pro"] == 1
    
    def test_estimate_cost_claude(self):
        """Test cost estimation for Claude model."""
        tracker = UsageTracker()
        
        cost = tracker._estimate_cost("claude-4-5-sonnet", 1_000_000, 500_000)
        
        # Claude pricing: $3 per 1M input, $15 per 1M output
        expected = (1 * 3.00) + (0.5 * 15.00)
        assert abs(cost - expected) < 0.01
    
    def test_estimate_cost_gemini(self):
        """Test cost estimation for Gemini model."""
        tracker = UsageTracker()
        
        cost = tracker._estimate_cost("gemini-2-5-pro", 1_000_000, 500_000)
        
        # Gemini pricing: $0.50 per 1M input, $1.50 per 1M output
        expected = (1 * 0.50) + (0.5 * 1.50)
        assert abs(cost - expected) < 0.01
    
    def test_estimate_cost_unknown_model(self):
        """Test cost estimation for unknown model (uses defaults)."""
        tracker = UsageTracker()
        
        cost = tracker._estimate_cost("unknown-model", 1_000_000, 500_000)
        
        # Should use default pricing
        assert cost > 0
    
    def test_generate_report(self):
        """Test generating usage report."""
        tracker = UsageTracker(session_id="test-session")
        
        tracker.track_request("claude-4-5-sonnet", 100, 50)
        tracker.track_request("gemini-2-5-pro", 200, 100)
        
        report = tracker.generate_report()
        
        assert report["session_id"] == "test-session"
        assert report["total_requests"] == 2
        assert report["total_input_tokens"] == 300
        assert report["total_output_tokens"] == 150
        assert report["total_tokens"] == 450
        assert report["estimated_cost_usd"] > 0
        assert report["start_time"] is not None
        assert report["end_time"] is not None
        assert "duration_seconds" in report
    
    def test_get_summary(self):
        """Test getting human-readable summary."""
        tracker = UsageTracker(session_id="test-session")
        
        tracker.track_request("claude-4-5-sonnet", 100, 50)
        
        summary = tracker.get_summary()
        
        assert "test-session" in summary
        assert "Requests: 1" in summary
        assert "Tokens: 150" in summary
        assert "Estimated Cost" in summary
    
    def test_reset(self):
        """Test resetting tracker."""
        tracker = UsageTracker(session_id="test-session")
        
        tracker.track_request("claude-4-5-sonnet", 100, 50)
        assert tracker.metrics.total_requests == 1
        
        tracker.reset()
        
        assert tracker.session_id != "test-session"
        assert tracker.metrics.total_requests == 0
        assert tracker.metrics.total_tokens == 0
        assert tracker.metrics.start_time is not None

