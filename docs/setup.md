# Setup Guide

This guide will walk you through setting up the Autonomous Agent Framework and creating your first agent implementation.

## Prerequisites

- Python 3.12 or higher (required for datetime.UTC)
- Git
- pip (Python package installer)
- A virtual environment tool (like venv)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/trevadelman/autonomous-agent-framework.git
cd autonomous-agent-framework
```

2. Create and activate a virtual environment:
```bash
# Create virtual environment with Python 3.12
python3.12 -m venv venv

# Activate on Unix/macOS
source venv/bin/activate

# Activate on Windows
.\venv\Scripts\activate
```

3. Install the package in development mode:
```bash
pip install -e ".[dev]"
```

4. Verify installation by running tests:
```bash
# Make sure to use Python 3.12 for running tests
python3.12 -m pytest
```

## Hello World Example

Here's a simple example that creates an agent that can respond to basic tasks:

1. Create a new file named `hello_world.py`:
```python
from autonomous_agent_framework import AutonomousAgent, AgentConfig, ModelType

async def main():
    # Create agent configuration
    config = AgentConfig(
        model=ModelType.GPT35_TURBO,
        system_prompt="You are a helpful assistant that can respond to basic tasks.",
        temperature=0.7
    )

    # Initialize agent
    agent = AutonomousAgent(config)

    # Execute a simple task
    response = await agent.execute("Say hello to the world and explain what you can do.")
    
    # Print the response
    print("Agent Response:")
    print(response.result)

    # Try a more complex task
    response = await agent.execute(
        "Create a list of 3 creative ways to say 'Hello World' in different programming languages."
    )
    
    print("\nCreative Response:")
    print(response.result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

2. Set up your OpenAI API key:
```bash
# Create .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

3. Run the example:
```bash
python3.12 hello_world.py
```

Expected output will look something like:
```
Agent Response:
Hello! I'm an AI assistant powered by the Autonomous Agent Framework. I can help you with various tasks such as:
- Answering questions and providing information
- Analyzing and solving problems
- Generating creative content
- Helping with basic programming tasks
Feel free to ask me anything!

Creative Response:
1. Python (using ASCII art):
   print('''
   ╔╗ ╔╗     ╔╗╔╗        ╔╗    ╔╗
   ║║ ║║     ║║║║        ║║    ║║
   ║╚═╝║╔══╗ ║║║║╔══╗    ║║ ╔══╝║
   ║╔═╗║║╔╗║ ║║║║║╔╗║    ║║ ║╔╗ ║
   ║║ ║║║║═╣ ║╚╝╚╣║║║    ║╚╗║╚╝ ║
   ╚╝ ╚╝╚══╝ ╚═══╩╝╚╝    ╚═╝╚══╗║
                                ╚═╝
   ''')

2. JavaScript (using console styling):
   console.log('%cHello %cWorld!', 
               'color: #FF6B6B; font-size: 20px;', 
               'color: #4ECDC4; font-size: 20px;')

3. Ruby (using string interpolation and emoji):
   puts "🌎 #{['Hello', 'World'].join(' ')} 👋"
```

## Next Steps

1. Explore the [Usage Guide](usage_guide.md) for more advanced examples
2. Check out the [API Documentation](api/core.md) for detailed information about available features
3. Review the [Tool Discovery](api/tools.md) documentation to learn how to extend the agent's capabilities

## Troubleshooting

1. If you encounter dependency issues:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

2. If OpenAI API calls fail:
- Verify your API key is correctly set in the .env file
- Check your OpenAI account has available credits
- Ensure you're using a supported model in the configuration

3. For other issues:
- Check the [GitHub Issues](https://github.com/trevadelman/autonomous-agent-framework/issues) page
- Run tests with verbose output: `pytest -v`
- Enable debug logging in your implementation:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Development Setup

If you want to contribute to the framework:

1. Fork the repository on GitHub
2. Create a new branch for your feature:
```bash
git checkout -b feature-name
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

4. Run tests before and after making changes:
```bash
python3.12 -m pytest
```

5. Submit a pull request with your changes

For more information about contributing, please see our [Contributing Guidelines](CONTRIBUTING.md).
