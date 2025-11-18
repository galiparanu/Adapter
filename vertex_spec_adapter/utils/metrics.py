"""Usage tracking and cost estimation for Vertex Spec Adapter."""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from vertex_spec_adapter.utils.logging import get_logger

logger = get_logger(__name__)


# Model pricing per 1M tokens (as of 2025-01-27)
# These are approximate and should be updated based on actual Vertex AI pricing
MODEL_PRICING = {
    "claude-4-5-sonnet": {
        "input": 3.00,  # $3 per 1M input tokens
        "output": 15.00,  # $15 per 1M output tokens
    },
    "claude-3-5-sonnet": {
        "input": 3.00,
        "output": 15.00,
    },
    "claude-3-opus": {
        "input": 15.00,
        "output": 75.00,
    },
    "gemini-2-5-pro": {
        "input": 0.50,  # $0.50 per 1M input tokens
        "output": 1.50,  # $1.50 per 1M output tokens
    },
    "gemini-1-5-pro": {
        "input": 0.50,
        "output": 1.50,
    },
    "gemini-1-5-flash": {
        "input": 0.075,
        "output": 0.30,
    },
    "qwen-coder": {
        "input": 0.10,  # Approximate pricing
        "output": 0.40,
    },
    "qwen-2-5-coder": {
        "input": 0.10,
        "output": 0.40,
    },
}


class UsageMetrics:
    """Container for usage metrics."""
    
    def __init__(self):
        """Initialize usage metrics."""
        self.total_requests = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_tokens = 0
        self.estimated_cost_usd = 0.0
        self.requests_by_model: Dict[str, int] = {}
        self.tokens_by_model: Dict[str, Dict[str, int]] = {}
        self.cost_by_model: Dict[str, float] = {}
        self.errors: List[Dict] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None


class UsageTracker:
    """
    Track token usage and estimate costs for Vertex AI API calls.
    
    Provides session-level tracking with cost estimation per model.
    """
    
    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize usage tracker.
        
        Args:
            session_id: Optional session identifier (UUID generated if not provided)
        """
        self.session_id = session_id or str(uuid4())
        self.metrics = UsageMetrics()
        self.metrics.start_time = datetime.utcnow()
        logger.info("Usage tracker initialized", session_id=self.session_id)
    
    def track_request(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: Optional[float] = None,
        error: Optional[Exception] = None
    ) -> None:
        """
        Track a single API request.
        
        Args:
            model: Model identifier used
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            latency_ms: Optional request latency in milliseconds
            error: Optional error that occurred
        """
        total_tokens = input_tokens + output_tokens
        
        # Update metrics
        self.metrics.total_requests += 1
        self.metrics.total_input_tokens += input_tokens
        self.metrics.total_output_tokens += output_tokens
        self.metrics.total_tokens += total_tokens
        
        # Track by model
        self.metrics.requests_by_model[model] = self.metrics.requests_by_model.get(model, 0) + 1
        
        if model not in self.metrics.tokens_by_model:
            self.metrics.tokens_by_model[model] = {"input": 0, "output": 0}
        self.metrics.tokens_by_model[model]["input"] += input_tokens
        self.metrics.tokens_by_model[model]["output"] += output_tokens
        
        # Calculate cost
        cost = self._estimate_cost(model, input_tokens, output_tokens)
        self.metrics.estimated_cost_usd += cost
        
        if model not in self.metrics.cost_by_model:
            self.metrics.cost_by_model[model] = 0.0
        self.metrics.cost_by_model[model] += cost
        
        # Track errors
        if error:
            self.metrics.errors.append({
                "timestamp": datetime.utcnow().isoformat(),
                "model": model,
                "error": str(error),
            })
        
        logger.info(
            "Request tracked",
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost_usd=cost,
            latency_ms=latency_ms,
        )
    
    def _estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate cost for a request.
        
        Args:
            model: Model identifier
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
        
        Returns:
            Estimated cost in USD
        """
        # Normalize model name (remove version suffix if present)
        model_key = model.split("@")[0].lower()
        
        # Get pricing for model
        pricing = MODEL_PRICING.get(model_key)
        if not pricing:
            # Use default pricing if model not found
            logger.warning("Model pricing not found, using defaults", model=model_key)
            pricing = {"input": 1.00, "output": 4.00}
        
        # Calculate cost
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        return input_cost + output_cost
    
    def generate_report(self) -> Dict:
        """
        Generate usage report for the session.
        
        Returns:
            Dictionary with usage statistics
        """
        self.metrics.end_time = datetime.utcnow()
        
        duration = None
        if self.metrics.start_time and self.metrics.end_time:
            duration = (self.metrics.end_time - self.metrics.start_time).total_seconds()
        
        report = {
            "session_id": self.session_id,
            "start_time": self.metrics.start_time.isoformat() if self.metrics.start_time else None,
            "end_time": self.metrics.end_time.isoformat() if self.metrics.end_time else None,
            "duration_seconds": duration,
            "total_requests": self.metrics.total_requests,
            "total_input_tokens": self.metrics.total_input_tokens,
            "total_output_tokens": self.metrics.total_output_tokens,
            "total_tokens": self.metrics.total_tokens,
            "estimated_cost_usd": round(self.metrics.estimated_cost_usd, 4),
            "requests_by_model": self.metrics.requests_by_model,
            "tokens_by_model": self.metrics.tokens_by_model,
            "cost_by_model": {
                model: round(cost, 4)
                for model, cost in self.metrics.cost_by_model.items()
            },
            "error_count": len(self.metrics.errors),
            "errors": self.metrics.errors if self.metrics.errors else None,
        }
        
        return report
    
    def get_summary(self) -> str:
        """
        Get human-readable summary of usage.
        
        Returns:
            Formatted summary string
        """
        report = self.generate_report()
        
        lines = [
            f"Session: {report['session_id']}",
            f"Requests: {report['total_requests']}",
            f"Tokens: {report['total_tokens']:,} (input: {report['total_input_tokens']:,}, output: {report['total_output_tokens']:,})",
            f"Estimated Cost: ${report['estimated_cost_usd']:.4f}",
        ]
        
        if report['requests_by_model']:
            lines.append("\nBy Model:")
            for model, count in report['requests_by_model'].items():
                tokens = report['tokens_by_model'].get(model, {})
                cost = report['cost_by_model'].get(model, 0.0)
                lines.append(
                    f"  {model}: {count} requests, "
                    f"{tokens.get('input', 0) + tokens.get('output', 0):,} tokens, "
                    f"${cost:.4f}"
                )
        
        if report['error_count'] > 0:
            lines.append(f"\nErrors: {report['error_count']}")
        
        return "\n".join(lines)
    
    def reset(self) -> None:
        """Reset all metrics (start new session)."""
        self.session_id = str(uuid4())
        self.metrics = UsageMetrics()
        self.metrics.start_time = datetime.utcnow()
        logger.info("Usage tracker reset", session_id=self.session_id)

