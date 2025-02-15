# Core API Documentation

## Agent Module

The agent module provides the base agent interface and concrete implementations for autonomous agents.

### Classes

#### `Agent` (Abstract Base Class)

Base class for all agents in the framework.

```python
class Agent(ABC):
    def __init__(self, config: AgentConfig):
        """Initialize agent with configuration."""
        
    async def execute(self, task: str) -> AgentResponse:
        """Execute a task and return the result."""
        
    async def discover_tools(self) -> List[Dict[str, Any]]:
        """Discover available tools that can be used by the agent."""
        
    async def request_credentials(self, tool_name: str, required_credentials: List[str]) -> Dict[str, str]:
        """Request necessary credentials from the user."""
```

#### `AutonomousAgent`

Main implementation of an autonomous agent with dynamic tool discovery.

```python
class AutonomousAgent(Agent):
    async def execute(self, task: str) -> AgentResponse:
        """Execute a task using the most appropriate tools and strategies."""
```

#### `AgentConfig`

Configuration model for agent instances.

```python
class AgentConfig(BaseModel):
    model: ModelType
    system_prompt: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    tools_allowed: bool = True
    auto_approve_safe_tools: bool = True
```

#### `AgentResponse`

Response model for agent execution results.

```python
class AgentResponse(BaseModel):
    success: bool
    result: Any
    error: Optional[str] = None
    tool_usage: List[Dict[str, Any]] = []
    model_used: ModelType
    tokens_used: Optional[int] = None
```

## Credentials Module

The credentials module provides secure credential management functionality.

### Classes

#### `CredentialManager`

Manages secure storage and retrieval of tool credentials.

```python
class CredentialManager:
    def __init__(self, app_name: str = "autonomous_agent_framework"):
        """Initialize credential manager."""
        
    async def store_credentials(
        self,
        tool_name: str,
        credentials: Dict[str, str],
        require_confirmation: bool = True
    ) -> bool:
        """Store credentials securely."""
        
    async def get_credentials(
        self,
        tool_name: str,
        required_keys: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """Retrieve stored credentials."""
        
    async def request_credentials(
        self,
        tool_name: str,
        required_credentials: List[str],
        descriptions: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """Request credentials from user."""
        
    async def clear_credentials(self, tool_name: str) -> bool:
        """Clear stored credentials for a tool."""
```

## Learning Module

The learning module provides functionality for tracking and learning from tool usage patterns.

### Classes

#### `LearningSystem`

System for tracking and learning from tool usage patterns.

```python
class LearningSystem:
    def __init__(self, storage_dir: Optional[Path] = None):
        """Initialize learning system."""
        
    async def record_tool_usage(self, metrics: ToolUsageMetrics) -> None:
        """Record a tool usage instance and update performance metrics."""
        
    async def get_tool_recommendations(
        self,
        context: Dict[str, Any],
        required_capabilities: Optional[Set[str]] = None
    ) -> List[str]:
        """Get recommended tools based on past performance and context."""
        
    async def get_tool_performance(self, tool_name: str) -> Optional[ToolPerformanceMetrics]:
        """Get performance metrics for a specific tool."""
        
    async def analyze_failure_patterns(self, tool_name: str) -> Dict[str, Any]:
        """Analyze patterns in tool failures."""
```

#### `ToolUsageMetrics`

Metrics for a single tool usage instance.

```python
class ToolUsageMetrics(BaseModel):
    tool_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    success: bool
    execution_time: float
    error_message: Optional[str] = None
    context: Dict[str, Any] = {}
    input_params: Dict[str, Any] = {}
    output_result: Optional[Dict[str, Any]] = None
```

## Security Module

The security module provides security and validation functionality.

### Classes

#### `ToolSecurity`

Security management for tool usage.

```python
class ToolSecurity:
    def __init__(
        self,
        config_dir: Optional[Path] = None,
        strict_mode: bool = True
    ):
        """Initialize security system."""
        
    async def set_tool_permissions(
        self,
        tool_name: str,
        permissions: Set[PermissionLevel]
    ) -> None:
        """Set permissions for a tool."""
        
    async def set_resource_limits(
        self,
        tool_name: str,
        limits: ResourceLimit
    ) -> None:
        """Set resource usage limits for a tool."""
        
    async def validate_tool_usage(
        self,
        tool_name: str,
        required_permissions: Set[PermissionLevel],
        resource_usage: Optional[Dict[str, float]] = None
    ) -> bool:
        """Validate if a tool can be used based on permissions and limits."""
        
    async def log_security_event(self, event: SecurityEvent) -> None:
        """Log a security-related event."""
        
    async def get_audit_logs(
        self,
        tool_name: Optional[str] = None,
        event_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[SecurityEvent]:
        """Get filtered security audit logs."""
```

#### `PermissionLevel`

Permission levels for tool access.

```python
class PermissionLevel(str, Enum):
    READ = "read"          # Can read data/files
    WRITE = "write"        # Can modify data/files
    EXECUTE = "execute"    # Can execute commands/tools
    NETWORK = "network"    # Can make network requests
    SYSTEM = "system"      # Can modify system settings
    ADMIN = "admin"        # Full access (includes all above)
```

#### `ResourceLimit`

Resource usage limits for tools.

```python
class ResourceLimit(BaseModel):
    max_memory_mb: Optional[int] = None
    max_cpu_percent: Optional[float] = None
    max_execution_time_sec: Optional[int] = None
    max_file_size_mb: Optional[int] = None
    max_network_requests: Optional[int] = None
    allowed_domains: Optional[List[str]] = None
    allowed_paths: Optional[List[str]] = None
