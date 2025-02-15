from typing import Dict, List, Optional, Set, Any
from datetime import datetime, UTC
import json
from pathlib import Path
from pydantic import BaseModel, Field


class ToolUsageMetrics(BaseModel):
    """Metrics for a single tool usage instance."""
    tool_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    success: bool
    execution_time: float  # in seconds
    error_message: Optional[str] = None
    context: Dict[str, Any] = {}
    input_params: Dict[str, Any] = {}
    output_result: Optional[Dict[str, Any]] = None


class ToolPerformanceMetrics(BaseModel):
    """Aggregated performance metrics for a tool."""
    total_uses: int = 0
    successful_uses: int = 0
    failed_uses: int = 0
    average_execution_time: float = 0.0
    last_used: Optional[datetime] = None
    common_errors: Dict[str, int] = {}  # error message -> count
    common_contexts: Dict[str, int] = {}  # context -> count


class LearningSystem:
    """System for tracking and learning from tool usage patterns."""

    def __init__(self, storage_dir: Optional[Path] = None):
        if storage_dir is None:
            storage_dir = Path.home() / ".config" / "autonomous_agent_framework" / "learning"
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache of performance metrics
        self._performance_cache: Dict[str, ToolPerformanceMetrics] = {}
        
        # Load existing metrics
        self._load_metrics()

    def _load_metrics(self) -> None:
        """Load existing performance metrics from storage."""
        metrics_file = self.storage_dir / "performance_metrics.json"
        if metrics_file.exists():
            try:
                data = json.loads(metrics_file.read_text())
                for tool_name, metrics in data.items():
                    self._performance_cache[tool_name] = ToolPerformanceMetrics.model_validate(metrics)
            except Exception as e:
                print(f"Error loading metrics: {e}")

    def _save_metrics(self) -> None:
        """Save current performance metrics to storage."""
        metrics_file = self.storage_dir / "performance_metrics.json"
        data = {
            tool_name: metrics.model_dump()
            for tool_name, metrics in self._performance_cache.items()
        }
        metrics_file.write_text(json.dumps(data, default=str, indent=2))

    async def record_tool_usage(self, metrics: ToolUsageMetrics) -> None:
        """Record a tool usage instance and update performance metrics.
        
        Args:
            metrics: Metrics for the tool usage instance
        """
        # Update performance metrics
        if metrics.tool_name not in self._performance_cache:
            self._performance_cache[metrics.tool_name] = ToolPerformanceMetrics()
        
        perf = self._performance_cache[metrics.tool_name]
        perf.total_uses += 1
        perf.last_used = metrics.timestamp
        
        if metrics.success:
            perf.successful_uses += 1
        else:
            perf.failed_uses += 1
            if metrics.error_message:
                perf.common_errors[metrics.error_message] = \
                    perf.common_errors.get(metrics.error_message, 0) + 1
        
        # Update average execution time
        perf.average_execution_time = (
            (perf.average_execution_time * (perf.total_uses - 1) + metrics.execution_time)
            / perf.total_uses
        )
        
        # Update context frequencies
        for context_key, context_value in metrics.context.items():
            context_str = f"{context_key}:{context_value}"
            perf.common_contexts[context_str] = \
                perf.common_contexts.get(context_str, 0) + 1
        
        # Save detailed usage log
        log_file = self.storage_dir / f"{metrics.tool_name}_usage.jsonl"
        with log_file.open("a") as f:
            f.write(json.dumps(metrics.model_dump(), default=str) + "\n")
        
        # Save updated performance metrics
        self._save_metrics()

    async def get_tool_recommendations(
        self,
        context: Dict[str, Any],
        required_capabilities: Optional[Set[str]] = None
    ) -> List[str]:
        """Get recommended tools based on past performance and current context.
        
        Args:
            context: Current execution context
            required_capabilities: Optional set of required tool capabilities
            
        Returns:
            List of recommended tool names, ordered by relevance
        """
        recommendations = []
        
        for tool_name, metrics in self._performance_cache.items():
            # Skip tools with no successful uses
            if metrics.successful_uses == 0:
                continue
            
            # Calculate base score from success rate
            success_rate = metrics.successful_uses / metrics.total_uses
            score = success_rate * 100
            
            # Boost score based on context matches
            context_matches = 0
            for ctx_key, ctx_value in context.items():
                context_str = f"{ctx_key}:{ctx_value}"
                if context_str in metrics.common_contexts:
                    context_matches += 1
                    score += 10 * (metrics.common_contexts[context_str] / metrics.total_uses)
            
            recommendations.append((tool_name, score))
        
        # Sort by score descending
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        return [tool_name for tool_name, _ in recommendations]

    async def get_tool_performance(self, tool_name: str) -> Optional[ToolPerformanceMetrics]:
        """Get performance metrics for a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            ToolPerformanceMetrics if tool exists, None otherwise
        """
        return self._performance_cache.get(tool_name)

    async def analyze_failure_patterns(self, tool_name: str) -> Dict[str, Any]:
        """Analyze patterns in tool failures.
        
        Args:
            tool_name: Name of the tool to analyze
            
        Returns:
            Dictionary containing failure analysis
        """
        if tool_name not in self._performance_cache:
            return {}
        
        metrics = self._performance_cache[tool_name]
        
        # Read detailed logs for failure analysis
        log_file = self.storage_dir / f"{tool_name}_usage.jsonl"
        if not log_file.exists():
            return {}
        
        failure_contexts = {}
        failure_params = {}
        
        with log_file.open() as f:
            for line in f:
                try:
                    usage = ToolUsageMetrics.model_validate_json(line)
                    if not usage.success:
                        # Track contexts that led to failures
                        for ctx_key, ctx_value in usage.context.items():
                            context_str = f"{ctx_key}:{ctx_value}"
                            failure_contexts[context_str] = \
                                failure_contexts.get(context_str, 0) + 1
                        
                        # Track parameters that led to failures
                        for param_key, param_value in usage.input_params.items():
                            param_str = f"{param_key}:{param_value}"
                            failure_params[param_str] = \
                                failure_params.get(param_str, 0) + 1
                except Exception:
                    continue
        
        return {
            "total_failures": metrics.failed_uses,
            "failure_rate": metrics.failed_uses / metrics.total_uses if metrics.total_uses > 0 else 0,
            "common_errors": dict(sorted(
                metrics.common_errors.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]),
            "failure_contexts": dict(sorted(
                failure_contexts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]),
            "failure_params": dict(sorted(
                failure_params.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5])
        }
