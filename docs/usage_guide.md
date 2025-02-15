# Usage Guide

This guide provides examples of how to use the Autonomous Agent Framework in common scenarios.

## Basic Usage

### Creating a Simple Agent

```python
from autonomous_agent_framework import AutonomousAgent, AgentConfig, ModelType

# Create agent configuration
config = AgentConfig(
    model=ModelType.GPT35_TURBO,
    system_prompt="You are a helpful agent that can use tools to accomplish tasks.",
    temperature=0.7
)

# Initialize agent
agent = AutonomousAgent(config)

# Execute a task
response = await agent.execute("Create a new directory named 'project' and initialize a git repository in it")
```

### Working with Credentials

```python
from autonomous_agent_framework import CredentialManager

# Initialize credential manager
cred_manager = CredentialManager()

# Store API credentials
github_creds = {
    "token": "your-github-token"
}
await cred_manager.store_credentials("github", github_creds)

# Retrieve credentials
creds = await cred_manager.get_credentials(
    "github",
    required_keys=["token"]
)

# Request credentials from user with descriptions
required_creds = ["api_key", "api_secret"]
descriptions = {
    "api_key": "Your API key from the developer dashboard",
    "api_secret": "Your API secret from the developer dashboard"
}
user_creds = await cred_manager.request_credentials(
    "my_api",
    required_creds,
    descriptions
)
```

### Security and Permissions

```python
from autonomous_agent_framework import (
    ToolSecurity,
    PermissionLevel,
    ResourceLimit
)

# Initialize security system
security = ToolSecurity()

# Set tool permissions
await security.set_tool_permissions(
    "git",
    {
        PermissionLevel.READ,
        PermissionLevel.WRITE,
        PermissionLevel.EXECUTE
    }
)

# Set resource limits
await security.set_resource_limits(
    "npm",
    ResourceLimit(
        max_memory_mb=1024,
        max_cpu_percent=50.0,
        max_execution_time_sec=300,
        allowed_domains=["npmjs.com", "github.com"]
    )
)

# Validate tool usage
can_use = await security.validate_tool_usage(
    "git",
    {PermissionLevel.EXECUTE},
    resource_usage={
        "memory_mb": 50,
        "cpu_percent": 25.0
    }
)
```

### Learning and Tool Recommendations

```python
from autonomous_agent_framework import LearningSystem, ToolUsageMetrics

# Initialize learning system
learning = LearningSystem()

# Record tool usage
await learning.record_tool_usage(ToolUsageMetrics(
    tool_name="git",
    success=True,
    execution_time=1.5,
    context={"operation": "clone", "repo_size": "small"},
    input_params={"url": "https://github.com/user/repo.git"}
))

# Get tool recommendations
recommendations = await learning.get_tool_recommendations(
    context={"operation": "clone"}
)

# Analyze failure patterns
analysis = await learning.analyze_failure_patterns("git")
```

## Common Scenarios

### Web Development Project

```python
# Initialize components
agent = AutonomousAgent(AgentConfig(
    model=ModelType.GPT4O_MINI,
    system_prompt="You are a web development assistant."
))
security = ToolSecurity()
learning = LearningSystem()

# Set up permissions
await security.set_tool_permissions(
    "npm",
    {PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.EXECUTE}
)
await security.set_tool_permissions(
    "git",
    {PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.EXECUTE}
)

# Execute tasks
tasks = [
    "Initialize a new React project named 'my-app'",
    "Add Material-UI as a dependency",
    "Create a basic layout component",
    "Set up routing with react-router"
]

for task in tasks:
    response = await agent.execute(task)
    if response.success:
        # Record successful tool usage
        for tool_usage in response.tool_usage:
            await learning.record_tool_usage(ToolUsageMetrics(
                tool_name=tool_usage["tool"],
                success=True,
                execution_time=tool_usage["duration"],
                context={"project_type": "react", "task": task}
            ))
```

### API Integration Project

```python
# Initialize components
agent = AutonomousAgent(AgentConfig(
    model=ModelType.O3_MINI,
    system_prompt="You are an API integration specialist."
))
cred_manager = CredentialManager()
security = ToolSecurity()

# Set up API credentials
api_creds = await cred_manager.request_credentials(
    "external_api",
    ["api_key", "api_secret"],
    {
        "api_key": "Your API key from the provider dashboard",
        "api_secret": "Your API secret from the provider dashboard"
    }
)

# Set up security
await security.set_tool_permissions(
    "external_api",
    {PermissionLevel.NETWORK, PermissionLevel.EXECUTE}
)
await security.set_resource_limits(
    "external_api",
    ResourceLimit(
        max_network_requests=100,
        allowed_domains=["api.provider.com"]
    )
)

# Execute integration task
response = await agent.execute(
    "Create a Python script that fetches data from the API and saves it to a CSV file"
)
```

### Data Analysis Project

```python
# Initialize components
agent = AutonomousAgent(AgentConfig(
    model=ModelType.O3_MINI,
    system_prompt="You are a data analysis specialist."
))
security = ToolSecurity()
learning = LearningSystem()

# Set up permissions for data tools
for tool in ["pandas", "numpy", "matplotlib"]:
    await security.set_tool_permissions(
        tool,
        {PermissionLevel.READ, PermissionLevel.EXECUTE}
    )
    await security.set_resource_limits(
        tool,
        ResourceLimit(
            max_memory_mb=2048,
            max_cpu_percent=75.0
        )
    )

# Execute analysis tasks
tasks = [
    "Load the dataset from data.csv",
    "Clean the data by removing duplicates and handling missing values",
    "Create visualizations of key metrics",
    "Generate a summary report"
]

for task in tasks:
    response = await agent.execute(task)
    if response.success:
        # Learn from successful tool usage
        for tool_usage in response.tool_usage:
            await learning.record_tool_usage(ToolUsageMetrics(
                tool_name=tool_usage["tool"],
                success=True,
                execution_time=tool_usage["duration"],
                context={"project_type": "data_analysis", "task": task}
            ))
```

## Best Practices

1. **Security First**
   - Always set appropriate permissions and resource limits
   - Use strict mode for security validation in production
   - Regularly audit security logs

2. **Credential Management**
   - Never hardcode credentials
   - Use the credential manager for all sensitive data
   - Regularly rotate credentials

3. **Learning System**
   - Record all tool usage for better recommendations
   - Include detailed context in usage metrics
   - Analyze failure patterns regularly

4. **Error Handling**
   - Always check response success status
   - Log and analyze failures
   - Implement appropriate retry strategies

5. **Resource Management**
   - Set appropriate resource limits
   - Monitor resource usage
   - Implement rate limiting for API calls
