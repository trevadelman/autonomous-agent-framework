# Autonomous Agent Framework

A flexible Python framework for creating autonomous agents that can discover and utilize tools dynamically.

## Project Philosophy

The Autonomous Agent Framework is built on several core principles:

1. **Dynamic Discovery**: Agents should be able to discover and adapt to available tools in their environment, rather than requiring explicit tool definitions.

2. **Security First**: All operations should be secure by default, with proper credential management, permissions, and resource limits.

3. **Learn and Adapt**: Agents should learn from their experiences, improving tool selection and usage over time.

4. **User Control**: While autonomous, agents should respect user-defined boundaries and always operate within specified constraints.

5. **Extensibility**: The framework should be easily extensible to support new tools, capabilities, and use cases.

## Core Goals

- Enable the creation of truly autonomous agents that can understand and utilize tools in their environment
- Provide robust security measures to ensure safe and controlled agent operations
- Implement learning mechanisms that improve agent performance over time
- Support a wide range of applications from simple automation to complex problem-solving
- Maintain high code quality with comprehensive testing and documentation

## Features

- 🔍 **Dynamic Tool Discovery**: Automatically discover and utilize available tools
- 🔐 **Secure Credential Management**: Safe storage and handling of sensitive data
- 📚 **Learning System**: Track usage patterns and get smart tool recommendations
- 🛡️ **Security & Validation**: Built-in permission system and resource limits
- 🔄 **Async Support**: Built for modern async/await patterns
- 📊 **Performance Monitoring**: Track and analyze tool usage metrics

## Quick Start

See our [Setup Guide](docs/setup.md) for detailed installation instructions and a Hello World example.

```bash
# Clone the repository
git clone https://github.com/trevadelman/autonomous-agent-framework.git

# Install the package
pip install -e ".[dev]"

# Create your first agent
from autonomous_agent_framework import AutonomousAgent, AgentConfig, ModelType

agent = AutonomousAgent(
    AgentConfig(
        model=ModelType.GPT35_TURBO,
        system_prompt="You are a helpful assistant."
    )
)
```

## Documentation

- [Setup Guide](docs/setup.md) - Get started with installation and basic usage
- [Usage Guide](docs/usage_guide.md) - Learn about advanced features and patterns
- [API Documentation](docs/api/core.md) - Detailed API reference
- [Tool Discovery](docs/api/tools.md) - Learn about the tool discovery system
- [Development Roadmap](docs/ROADMAP.md) - See our development plans and progress

## Requirements

- Python 3.8+
- OpenAI API key for model access
- Modern Python tooling (pip, venv)

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Security

For security concerns, please file a private issue or contact the maintainers directly.
