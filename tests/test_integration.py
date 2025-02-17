import pytest
from pathlib import Path
import json
from datetime import datetime, UTC

from autonomous_agent_framework.core.agent import (
    AutonomousAgent,
    AgentConfig,
    ModelType
)
from autonomous_agent_framework.tools.discovery import (
    ToolDiscovery,
    ToolCategory,
    ToolCapability
)
from autonomous_agent_framework.core.credentials import CredentialManager
from autonomous_agent_framework.core.learning import (
    LearningSystem,
    ToolUsageMetrics
)
from autonomous_agent_framework.core.security import (
    ToolSecurity,
    PermissionLevel,
    ResourceLimit
)

@pytest.fixture
def temp_config_dir(tmp_path):
    """Create temporary configuration directory."""
    config_dir = tmp_path / ".config" / "test_framework"
    config_dir.mkdir(parents=True)
    return config_dir

@pytest.fixture
def agent_config():
    """Create agent configuration."""
    return AgentConfig(
        model=ModelType.GPT35_TURBO,
        system_prompt="You are a helpful agent that can use tools to accomplish tasks."
    )

@pytest.fixture
def tool_discovery():
    """Create tool discovery instance."""
    return ToolDiscovery()

@pytest.fixture
def credential_manager(temp_config_dir):
    """Create credential manager instance."""
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(Path, "home", lambda: temp_config_dir.parent.parent)
        # Mock getpass to avoid password prompt
        mp.setattr("getpass.getpass", lambda _: "test_password")
        # Use a simple in-memory dict for testing
        import keyring
        class TestKeyring(keyring.backend.KeyringBackend):
            """Simple in-memory keyring for testing."""
            def __init__(self):
                self.passwords = {}

            def get_password(self, servicename, username):
                return self.passwords.get((servicename, username))

            def set_password(self, servicename, username, password):
                self.passwords[(servicename, username)] = password

            def delete_password(self, servicename, username):
                self.passwords.pop((servicename, username), None)

        keyring.set_keyring(TestKeyring())
        return CredentialManager(app_name="test_framework")

@pytest.fixture
def learning_system(temp_config_dir):
    """Create learning system instance."""
    return LearningSystem(storage_dir=temp_config_dir / "learning")

@pytest.fixture
def security_system(temp_config_dir):
    """Create security system instance."""
    return ToolSecurity(config_dir=temp_config_dir / "security")

class TestIntegration:
    @pytest.mark.asyncio
    async def test_tool_discovery_with_credentials(
        self,
        tool_discovery,
        credential_manager
    ):
        """Test tool discovery with credential management."""
        # Mock discovering a tool that needs credentials
        test_creds = {
            "api_key": "test_key",
            "secret": "test_secret"
        }
        
        # Store credentials
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr("builtins.input", lambda _: "y")
            await credential_manager.store_credentials("test_api", test_creds)
        
        # Verify credentials can be retrieved
        retrieved = await credential_manager.get_credentials(
            "test_api",
            required_keys=["api_key", "secret"]
        )
        assert retrieved == test_creds

    @pytest.mark.asyncio
    async def test_tool_usage_with_security_and_learning(
        self,
        security_system,
        learning_system
    ):
        """Test tool usage with security validation and learning."""
        # Set up tool permissions and limits
        await security_system.set_tool_permissions(
            "test_tool",
            {PermissionLevel.EXECUTE}
        )
        await security_system.set_resource_limits(
            "test_tool",
            ResourceLimit(
                max_memory_mb=100,
                max_cpu_percent=50.0
            )
        )
        
        # Record successful tool usage
        await learning_system.record_tool_usage(ToolUsageMetrics(
            tool_name="test_tool",
            success=True,
            execution_time=1.0,
            context={"task": "test_task"}
        ))
        
        # Validate tool usage with security
        assert await security_system.validate_tool_usage(
            "test_tool",
            {PermissionLevel.EXECUTE},
            resource_usage={
                "memory_mb": 50,
                "cpu_percent": 25.0
            }
        )
        
        # Get tool recommendations
        recommendations = await learning_system.get_tool_recommendations(
            context={"task": "test_task"}
        )
        assert "test_tool" in recommendations

    @pytest.mark.asyncio
    async def test_end_to_end_workflow(
        self,
        agent_config,
        tool_discovery,
        credential_manager,
        learning_system,
        security_system
    ):
        """Test complete end-to-end workflow."""
        # Set up security permissions
        await security_system.set_tool_permissions(
            "file_ops",
            {
                PermissionLevel.READ,
                PermissionLevel.WRITE
            }
        )
        
        # Create a test file
        test_file = Path("test.txt")
        test_file.write_text("Hello, World!")
        
        try:
            # Record tool usage
            await learning_system.record_tool_usage(ToolUsageMetrics(
                tool_name="file_ops",
                success=True,
                execution_time=0.1,
                context={"operation": "write"},
                input_params={"path": str(test_file)}
            ))
            
            # Verify tool was learned
            recommendations = await learning_system.get_tool_recommendations(
                context={"operation": "write"}
            )
            assert "file_ops" in recommendations
            
            # Verify security audit logs
            audit_logs = await security_system.get_audit_logs(
                tool_name="file_ops"
            )
            assert len(audit_logs) > 0
            
        finally:
            # Cleanup
            if test_file.exists():
                test_file.unlink()

    @pytest.mark.asyncio
    async def test_error_handling(
        self,
        security_system,
        learning_system
    ):
        """Test error handling across components."""
        # Try to use tool without permissions
        with pytest.raises(Exception):
            await security_system.validate_tool_usage(
                "undefined_tool",
                {PermissionLevel.EXECUTE}
            )
        
        # Record failed usage
        await learning_system.record_tool_usage(ToolUsageMetrics(
            tool_name="undefined_tool",
            success=False,
            execution_time=0.1,
            error_message="Permission denied"
        ))
        
        # Analyze failure patterns
        analysis = await learning_system.analyze_failure_patterns("undefined_tool")
        assert analysis["total_failures"] == 1
        assert "Permission denied" in analysis["common_errors"]

    @pytest.mark.asyncio
    async def test_performance_monitoring(
        self,
        learning_system,
        security_system
    ):
        """Test performance monitoring and resource limits."""
        # Set up permissions and resource limits
        await security_system.set_tool_permissions(
            "test_tool",
            {PermissionLevel.EXECUTE}
        )
        
        await security_system.set_resource_limits(
            "test_tool",
            ResourceLimit(
                max_memory_mb=100,
                max_cpu_percent=50.0,
                max_execution_time_sec=5
            )
        )
        
        # Record usage with performance metrics
        await learning_system.record_tool_usage(ToolUsageMetrics(
            tool_name="test_tool",
            success=True,
            execution_time=1.0,
            context={"load": "low"},
            resource_usage={
                "memory_mb": 50,
                "cpu_percent": 25.0
            }
        ))
        
        # Get tool performance
        perf = await learning_system.get_tool_performance("test_tool")
        assert perf is not None
        assert perf.average_execution_time == 1.0
        
        # Verify resource limits
        assert await security_system.validate_tool_usage(
            "test_tool",
            {PermissionLevel.EXECUTE},  # Need execute permission
            resource_usage={
                "memory_mb": 50,
                "cpu_percent": 25.0
            }
        )
