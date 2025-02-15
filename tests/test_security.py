import pytest
from pathlib import Path
import json
from datetime import datetime, UTC, timedelta

from autonomous_agent_framework.core.security import (
    ToolSecurity,
    PermissionLevel,
    ResourceLimit,
    SecurityEvent,
    SecurityError
)

@pytest.fixture
def temp_security_dir(tmp_path):
    """Create a temporary directory for security data."""
    security_dir = tmp_path / "security"
    security_dir.mkdir()
    return security_dir

@pytest.fixture
def security_system(temp_security_dir):
    """Create a ToolSecurity instance with a temporary directory."""
    return ToolSecurity(config_dir=temp_security_dir)

class TestToolSecurity:
    @pytest.mark.asyncio
    async def test_set_tool_permissions(self, security_system, temp_security_dir):
        """Test setting and saving tool permissions."""
        permissions = {
            PermissionLevel.READ,
            PermissionLevel.WRITE,
            PermissionLevel.EXECUTE
        }
        
        await security_system.set_tool_permissions("test_tool", permissions)
        
        # Verify permissions were saved
        perms_file = temp_security_dir / "permissions.json"
        assert perms_file.exists()
        
        saved_data = json.loads(perms_file.read_text())
        assert "test_tool" in saved_data
        assert set(saved_data["test_tool"]) == {p.value for p in permissions}
        
        # Verify audit log was created
        log_file = temp_security_dir / "security_audit.jsonl"
        assert log_file.exists()
        
        log_entry = json.loads(log_file.read_text())
        assert log_entry["event_type"] == "permission_update"
        assert log_entry["tool_name"] == "test_tool"
        assert log_entry["status"] == "success"

    @pytest.mark.asyncio
    async def test_set_resource_limits(self, security_system):
        """Test setting resource limits."""
        limits = ResourceLimit(
            max_memory_mb=1024,
            max_cpu_percent=50.0,
            max_execution_time_sec=300,
            allowed_domains=["example.com"]
        )
        
        await security_system.set_resource_limits("test_tool", limits)
        
        # Verify limits were saved
        saved_limits = security_system._resource_limits["test_tool"]
        assert saved_limits.max_memory_mb == 1024
        assert saved_limits.max_cpu_percent == 50.0
        assert saved_limits.max_execution_time_sec == 300
        assert saved_limits.allowed_domains == ["example.com"]

    @pytest.mark.asyncio
    async def test_validate_tool_usage_permissions(self, security_system):
        """Test tool usage validation based on permissions."""
        # Set up permissions
        await security_system.set_tool_permissions(
            "test_tool",
            {PermissionLevel.READ, PermissionLevel.WRITE}
        )
        
        # Test allowed permissions
        assert await security_system.validate_tool_usage(
            "test_tool",
            {PermissionLevel.READ}
        )
        
        # Test missing permissions
        with pytest.raises(SecurityError):
            await security_system.validate_tool_usage(
                "test_tool",
                {PermissionLevel.EXECUTE}
            )
        
        # Test undefined tool
        with pytest.raises(SecurityError):
            await security_system.validate_tool_usage(
                "undefined_tool",
                {PermissionLevel.READ}
            )

    @pytest.mark.asyncio
    async def test_validate_tool_usage_resources(self, security_system):
        """Test tool usage validation based on resource limits."""
        # Set up permissions and limits
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
        
        # Test within limits
        assert await security_system.validate_tool_usage(
            "test_tool",
            {PermissionLevel.EXECUTE},
            resource_usage={
                "memory_mb": 50,
                "cpu_percent": 25.0
            }
        )
        
        # Test exceeding memory limit
        with pytest.raises(SecurityError):
            await security_system.validate_tool_usage(
                "test_tool",
                {PermissionLevel.EXECUTE},
                resource_usage={
                    "memory_mb": 200,
                    "cpu_percent": 25.0
                }
            )
        
        # Test exceeding CPU limit
        with pytest.raises(SecurityError):
            await security_system.validate_tool_usage(
                "test_tool",
                {PermissionLevel.EXECUTE},
                resource_usage={
                    "memory_mb": 50,
                    "cpu_percent": 75.0
                }
            )

    @pytest.mark.asyncio
    async def test_admin_permission(self, security_system):
        """Test that admin permission grants all access."""
        await security_system.set_tool_permissions(
            "admin_tool",
            {PermissionLevel.ADMIN}
        )
        
        # Admin should have access to everything
        assert await security_system.validate_tool_usage(
            "admin_tool",
            {
                PermissionLevel.READ,
                PermissionLevel.WRITE,
                PermissionLevel.EXECUTE,
                PermissionLevel.NETWORK,
                PermissionLevel.SYSTEM
            }
        )

    @pytest.mark.asyncio
    async def test_audit_logging_and_filtering(self, security_system):
        """Test security audit logging and log filtering."""
        # Create some events
        event1 = SecurityEvent(
            event_type="access",
            tool_name="tool1",
            user="user1",
            action="read",
            status="success"
        )
        
        event2 = SecurityEvent(
            event_type="access",
            tool_name="tool2",
            user="user1",
            action="write",
            status="denied",
            timestamp=datetime.now(UTC) - timedelta(hours=1)
        )
        
        await security_system.log_security_event(event1)
        await security_system.log_security_event(event2)
        
        # Test filtering by tool
        tool1_logs = await security_system.get_audit_logs(tool_name="tool1")
        assert len(tool1_logs) == 1
        assert tool1_logs[0].tool_name == "tool1"
        
        # Test filtering by event type
        access_logs = await security_system.get_audit_logs(event_type="access")
        assert len(access_logs) == 2
        
        # Test filtering by time range
        recent_logs = await security_system.get_audit_logs(
            start_time=datetime.now(UTC) - timedelta(minutes=30)
        )
        assert len(recent_logs) == 1
        assert recent_logs[0].tool_name == "tool1"

    @pytest.mark.asyncio
    async def test_non_strict_mode(self, temp_security_dir):
        """Test security system in non-strict mode."""
        security = ToolSecurity(
            config_dir=temp_security_dir,
            strict_mode=False
        )
        
        # Missing permissions should return False instead of raising
        result = await security.validate_tool_usage(
            "undefined_tool",
            {PermissionLevel.READ}
        )
        assert result is False
        
        # Set up tool with limits
        await security.set_tool_permissions(
            "test_tool",
            {PermissionLevel.EXECUTE}
        )
        await security.set_resource_limits(
            "test_tool",
            ResourceLimit(max_memory_mb=100)
        )
        
        # Exceeding limits should return False instead of raising
        result = await security.validate_tool_usage(
            "test_tool",
            {PermissionLevel.EXECUTE},
            resource_usage={"memory_mb": 200}
        )
        assert result is False
