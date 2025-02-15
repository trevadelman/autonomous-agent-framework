from typing import Dict, List, Optional, Set, Any
from enum import Enum
from pathlib import Path
import json
from datetime import datetime, UTC
from pydantic import BaseModel, Field


class PermissionLevel(str, Enum):
    """Permission levels for tool access."""
    READ = "read"          # Can read data/files
    WRITE = "write"        # Can modify data/files
    EXECUTE = "execute"    # Can execute commands/tools
    NETWORK = "network"    # Can make network requests
    SYSTEM = "system"      # Can modify system settings
    ADMIN = "admin"        # Full access (includes all above)


class ResourceLimit(BaseModel):
    """Resource usage limits for tools."""
    max_memory_mb: Optional[int] = None
    max_cpu_percent: Optional[float] = None
    max_execution_time_sec: Optional[int] = None
    max_file_size_mb: Optional[int] = None
    max_network_requests: Optional[int] = None
    allowed_domains: Optional[List[str]] = None
    allowed_paths: Optional[List[str]] = None


class SecurityEvent(BaseModel):
    """Security-related event for audit logging."""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    event_type: str
    tool_name: str
    user: str
    action: str
    status: str  # success, denied, error
    details: Dict[str, Any] = {}
    resource_usage: Optional[Dict[str, float]] = None


class ToolSecurity:
    """Security management for tool usage."""

    def __init__(
        self,
        config_dir: Optional[Path] = None,
        strict_mode: bool = True
    ):
        if config_dir is None:
            config_dir = Path.home() / ".config" / "autonomous_agent_framework" / "security"
        self.config_dir = config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.strict_mode = strict_mode
        self._permissions: Dict[str, Set[PermissionLevel]] = {}
        self._resource_limits: Dict[str, ResourceLimit] = {}
        
        # Load existing configurations
        self._load_config()

    def _load_config(self) -> None:
        """Load security configurations from storage."""
        # Load permissions
        perms_file = self.config_dir / "permissions.json"
        if perms_file.exists():
            try:
                data = json.loads(perms_file.read_text())
                for tool_name, perms in data.items():
                    self._permissions[tool_name] = {
                        PermissionLevel(p) for p in perms
                    }
            except Exception as e:
                print(f"Error loading permissions: {e}")
        
        # Load resource limits
        limits_file = self.config_dir / "resource_limits.json"
        if limits_file.exists():
            try:
                data = json.loads(limits_file.read_text())
                for tool_name, limits in data.items():
                    self._resource_limits[tool_name] = ResourceLimit.model_validate(limits)
            except Exception as e:
                print(f"Error loading resource limits: {e}")

    def _save_config(self) -> None:
        """Save security configurations to storage."""
        # Save permissions
        perms_file = self.config_dir / "permissions.json"
        perms_data = {
            tool_name: [p.value for p in perms]
            for tool_name, perms in self._permissions.items()
        }
        perms_file.write_text(json.dumps(perms_data, indent=2))
        
        # Save resource limits
        limits_file = self.config_dir / "resource_limits.json"
        limits_data = {
            tool_name: limits.model_dump()
            for tool_name, limits in self._resource_limits.items()
        }
        limits_file.write_text(json.dumps(limits_data, indent=2))

    async def set_tool_permissions(
        self,
        tool_name: str,
        permissions: Set[PermissionLevel]
    ) -> None:
        """Set permissions for a tool.
        
        Args:
            tool_name: Name of the tool
            permissions: Set of permission levels to grant
        """
        self._permissions[tool_name] = permissions
        self._save_config()
        await self.log_security_event(SecurityEvent(
            event_type="permission_update",
            tool_name=tool_name,
            user="system",
            action="set_permissions",
            status="success",
            details={"permissions": [p.value for p in permissions]}
        ))

    async def set_resource_limits(
        self,
        tool_name: str,
        limits: ResourceLimit
    ) -> None:
        """Set resource usage limits for a tool.
        
        Args:
            tool_name: Name of the tool
            limits: Resource limits to enforce
        """
        self._resource_limits[tool_name] = limits
        self._save_config()
        await self.log_security_event(SecurityEvent(
            event_type="limits_update",
            tool_name=tool_name,
            user="system",
            action="set_limits",
            status="success",
            details=limits.model_dump()
        ))

    async def validate_tool_usage(
        self,
        tool_name: str,
        required_permissions: Set[PermissionLevel],
        resource_usage: Optional[Dict[str, float]] = None
    ) -> bool:
        """Validate if a tool can be used based on permissions and limits.
        
        Args:
            tool_name: Name of the tool
            required_permissions: Permissions needed for the operation
            resource_usage: Optional dict of resource usage metrics
            
        Returns:
            bool: True if usage is allowed, False otherwise
            
        Raises:
            SecurityError: If validation fails in strict mode
        """
        # Check permissions
        if tool_name not in self._permissions:
            if self.strict_mode:
                raise SecurityError(f"No permissions defined for tool: {tool_name}")
            return False
        
        tool_perms = self._permissions[tool_name]
        if PermissionLevel.ADMIN not in tool_perms:
            missing_perms = required_permissions - tool_perms
            if missing_perms:
                if self.strict_mode:
                    raise SecurityError(
                        f"Missing permissions for {tool_name}: {missing_perms}"
                    )
                return False
        
        # Check resource limits if usage provided
        if resource_usage and tool_name in self._resource_limits:
            limits = self._resource_limits[tool_name]
            
            if (limits.max_memory_mb and 
                resource_usage.get("memory_mb", 0) > limits.max_memory_mb):
                if self.strict_mode:
                    raise SecurityError(f"Memory limit exceeded for {tool_name}")
                return False
            
            if (limits.max_cpu_percent and 
                resource_usage.get("cpu_percent", 0) > limits.max_cpu_percent):
                if self.strict_mode:
                    raise SecurityError(f"CPU limit exceeded for {tool_name}")
                return False
            
            if (limits.max_execution_time_sec and 
                resource_usage.get("execution_time_sec", 0) > limits.max_execution_time_sec):
                if self.strict_mode:
                    raise SecurityError(f"Execution time limit exceeded for {tool_name}")
                return False
        
        return True

    async def log_security_event(self, event: SecurityEvent) -> None:
        """Log a security-related event.
        
        Args:
            event: Security event to log
        """
        log_file = self.config_dir / "security_audit.jsonl"
        with log_file.open("a") as f:
            f.write(json.dumps(event.model_dump(), default=str) + "\n")

    async def get_audit_logs(
        self,
        tool_name: Optional[str] = None,
        event_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[SecurityEvent]:
        """Get filtered security audit logs.
        
        Args:
            tool_name: Optional tool name to filter by
            event_type: Optional event type to filter by
            start_time: Optional start time for time range
            end_time: Optional end time for time range
            
        Returns:
            List of matching security events
        """
        log_file = self.config_dir / "security_audit.jsonl"
        if not log_file.exists():
            return []
        
        events = []
        with log_file.open() as f:
            for line in f:
                try:
                    event = SecurityEvent.model_validate_json(line)
                    
                    # Apply filters
                    if tool_name and event.tool_name != tool_name:
                        continue
                    if event_type and event.event_type != event_type:
                        continue
                    if start_time and event.timestamp < start_time:
                        continue
                    if end_time and event.timestamp > end_time:
                        continue
                    
                    events.append(event)
                except Exception:
                    continue
        
        return events


class SecurityError(Exception):
    """Error raised for security violations."""
    pass
