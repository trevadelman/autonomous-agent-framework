import pytest
from pathlib import Path
import json
from datetime import datetime, timedelta

from autonomous_agent_framework.core.learning import (
    LearningSystem,
    ToolUsageMetrics,
    ToolPerformanceMetrics
)

@pytest.fixture
def temp_learning_dir(tmp_path):
    """Create a temporary directory for learning data."""
    learning_dir = tmp_path / "learning"
    learning_dir.mkdir()
    return learning_dir

@pytest.fixture
def learning_system(temp_learning_dir):
    """Create a LearningSystem instance with a temporary directory."""
    return LearningSystem(storage_dir=temp_learning_dir)

class TestLearningSystem:
    @pytest.mark.asyncio
    async def test_record_tool_usage(self, learning_system, temp_learning_dir):
        """Test recording tool usage metrics."""
        metrics = ToolUsageMetrics(
            tool_name="test_tool",
            success=True,
            execution_time=1.5,
            context={"task": "test_task"},
            input_params={"param1": "value1"}
        )
        
        await learning_system.record_tool_usage(metrics)
        
        # Verify performance metrics were updated
        perf = await learning_system.get_tool_performance("test_tool")
        assert perf is not None
        assert perf.total_uses == 1
        assert perf.successful_uses == 1
        assert perf.failed_uses == 0
        assert perf.average_execution_time == 1.5
        assert "task:test_task" in perf.common_contexts
        
        # Verify metrics were saved to file
        metrics_file = temp_learning_dir / "performance_metrics.json"
        assert metrics_file.exists()
        
        # Verify usage log was created
        log_file = temp_learning_dir / "test_tool_usage.jsonl"
        assert log_file.exists()
        
        # Verify log content
        log_entry = json.loads(log_file.read_text())
        assert log_entry["tool_name"] == "test_tool"
        assert log_entry["success"] is True
        assert log_entry["execution_time"] == 1.5

    @pytest.mark.asyncio
    async def test_record_tool_failure(self, learning_system):
        """Test recording tool failure metrics."""
        metrics = ToolUsageMetrics(
            tool_name="test_tool",
            success=False,
            execution_time=0.5,
            error_message="Test error",
            context={"task": "failed_task"}
        )
        
        await learning_system.record_tool_usage(metrics)
        
        perf = await learning_system.get_tool_performance("test_tool")
        assert perf is not None
        assert perf.total_uses == 1
        assert perf.successful_uses == 0
        assert perf.failed_uses == 1
        assert "Test error" in perf.common_errors
        assert perf.common_errors["Test error"] == 1

    @pytest.mark.asyncio
    async def test_get_tool_recommendations(self, learning_system):
        """Test tool recommendations based on context."""
        # Record successful uses in different contexts
        await learning_system.record_tool_usage(ToolUsageMetrics(
            tool_name="tool1",
            success=True,
            execution_time=1.0,
            context={"task": "task1", "env": "prod"}
        ))
        
        await learning_system.record_tool_usage(ToolUsageMetrics(
            tool_name="tool2",
            success=True,
            execution_time=1.0,
            context={"task": "task2", "env": "dev"}
        ))
        
        # Record some failures
        await learning_system.record_tool_usage(ToolUsageMetrics(
            tool_name="tool2",
            success=False,
            execution_time=1.0,
            context={"task": "task2", "env": "prod"}
        ))
        
        # Get recommendations for different contexts
        prod_recommendations = await learning_system.get_tool_recommendations(
            context={"env": "prod"}
        )
        assert "tool1" in prod_recommendations
        if "tool2" in prod_recommendations:
            assert prod_recommendations.index("tool1") < prod_recommendations.index("tool2")
        
        dev_recommendations = await learning_system.get_tool_recommendations(
            context={"env": "dev"}
        )
        assert "tool2" in dev_recommendations

    @pytest.mark.asyncio
    async def test_analyze_failure_patterns(self, learning_system):
        """Test analyzing patterns in tool failures."""
        # Record multiple failures with patterns
        for _ in range(3):
            await learning_system.record_tool_usage(ToolUsageMetrics(
                tool_name="test_tool",
                success=False,
                execution_time=1.0,
                error_message="Connection error",
                context={"env": "prod"},
                input_params={"timeout": 30}
            ))
        
        await learning_system.record_tool_usage(ToolUsageMetrics(
            tool_name="test_tool",
            success=False,
            execution_time=1.0,
            error_message="Authentication error",
            context={"env": "dev"},
            input_params={"timeout": 60}
        ))
        
        analysis = await learning_system.analyze_failure_patterns("test_tool")
        
        assert analysis["total_failures"] == 4
        assert analysis["failure_rate"] == 1.0  # All attempts failed
        assert "Connection error" in analysis["common_errors"]
        assert analysis["common_errors"]["Connection error"] == 3
        assert "env:prod" in analysis["failure_contexts"]
        assert "timeout:30" in analysis["failure_params"]

    @pytest.mark.asyncio
    async def test_persistence(self, learning_system, temp_learning_dir):
        """Test that metrics persist between system instances."""
        # Record some metrics
        await learning_system.record_tool_usage(ToolUsageMetrics(
            tool_name="test_tool",
            success=True,
            execution_time=1.0
        ))
        
        # Create new instance with same directory
        new_system = LearningSystem(storage_dir=temp_learning_dir)
        
        # Verify metrics were loaded
        perf = await new_system.get_tool_performance("test_tool")
        assert perf is not None
        assert perf.total_uses == 1
        assert perf.successful_uses == 1

    @pytest.mark.asyncio
    async def test_average_execution_time(self, learning_system):
        """Test calculation of average execution time."""
        await learning_system.record_tool_usage(ToolUsageMetrics(
            tool_name="test_tool",
            success=True,
            execution_time=1.0
        ))
        
        await learning_system.record_tool_usage(ToolUsageMetrics(
            tool_name="test_tool",
            success=True,
            execution_time=2.0
        ))
        
        perf = await learning_system.get_tool_performance("test_tool")
        assert perf is not None
        assert perf.average_execution_time == 1.5  # (1.0 + 2.0) / 2
