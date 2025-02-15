# Autonomous Agent Framework

A flexible and intelligent Python framework for creating autonomous agents that can discover, learn, and utilize tools dynamically to accomplish tasks.

## Philosophy

Traditional agent frameworks require explicit tool definitions and rigid structures. This framework takes a different approach by enabling agents to:
1. Dynamically discover available tools and capabilities
2. Request necessary credentials or information when needed
3. Learn from usage patterns to improve tool selection
4. Maintain security while having flexibility

## Key Features

### Dynamic Tool Discovery
- Automatic scanning of system capabilities
- Understanding of tool documentation and requirements
- Smart matching of tools to task requirements

### Intelligent Tool Selection
- Context-aware tool recommendations
- Learning from successful patterns
- Adaptation to user preferences

### Secure Credential Management
- Safe storage of API keys and credentials
- Just-in-time credential requests
- Encrypted storage with proper scope isolation

### Learning System
- Pattern recognition in successful tool usage
- Improvement through experience
- Knowledge sharing between tasks

## Basic Usage

```python
# Create an autonomous agent
agent = AutonomousAgent(
    model="gpt-4o-mini",  # Choose model based on task requirements
    system_prompt="You are a capable agent that can accomplish tasks..."
)

# Execute a task
result = agent.execute("Create a React website with a todo list")

# Agent will:
# 1. Discover available tools (npm, file operations, etc.)
# 2. Request any needed credentials
# 3. Execute the task using optimal tools
# 4. Learn from the experience

# Example with different model for complex reasoning
agent_complex = AutonomousAgent(
    model="o3-mini",  # Better for tasks requiring deep analysis
    system_prompt="You are an agent specialized in complex problem-solving..."
)
```

## Installation

```bash
pip install autonomous-agent-framework  # Coming soon
```

## Requirements

- Python 3.8+
- OpenAI API key for model integration:
  - GPT-3.5 Turbo: Fast, cost-effective for routine tasks
  - GPT-4o mini: Multimodal capabilities (text, image, audio)
  - o3-mini: Advanced reasoning and complex logic
  - DALL-E: Image generation (optional)
  - Whisper: Audio transcription (optional)

See our [Model Selection Guide](docs/ModelSelection.md) for detailed comparisons and use cases.

## Model Selection

The framework supports multiple OpenAI models, each optimized for different use cases:

- **GPT-3.5 Turbo**: Best for high-volume, routine tasks where cost-efficiency is priority
- **GPT-4o mini**: Ideal for tasks requiring multimodal processing (text, image, audio)
- **o3-mini**: Recommended for complex reasoning and advanced problem-solving
- **DALL-E**: Available for image generation tasks
- **Whisper**: Integrated for audio transcription needs

The framework automatically suggests the most appropriate model based on task requirements and past performance patterns.

## Security Considerations

The framework prioritizes security through:
- Tool usage validation
- Credential encryption
- Permission scoping
- User confirmation for sensitive operations

## Contributing

We welcome contributions! See our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - See [LICENSE](LICENSE) for details.
