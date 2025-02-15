# Framework Examples

This directory contains example implementations and demonstrations of the Autonomous Agent Framework.

## Demo Agent

The `demo_agent.py` script demonstrates the core features of the framework:

1. **Agent Configuration and Initialization**
   - Setting up an agent with GPT-3.5 Turbo
   - Configuring system prompts and parameters

2. **Security System**
   - Setting up tool permissions
   - Configuring resource limits
   - Validating tool usage

3. **Credential Management**
   - Storing credentials securely
   - Retrieving credentials with validation

4. **Learning System**
   - Recording tool usage metrics
   - Getting tool recommendations
   - Analyzing performance metrics

5. **Task Execution**
   - Basic creative tasks
   - File operations
   - Complex analysis tasks

### Running the Demo

1. Set up your environment:
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Unix/macOS
# or
.\venv\Scripts\activate  # Windows

# Install the framework
pip install -e ".[dev]"
```

2. Set up your OpenAI API key:
```bash
# Create .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

3. Run the demo:
```bash
python examples/demo_agent.py
```

### Expected Output

The demo will output logs showing:
- Agent initialization
- Task execution results
- Security validations
- Credential management operations
- Tool recommendations
- Performance metrics

Example output:
```
INFO:__main__:Agent initialized successfully

=== Test 1: Basic Task ===
INFO:__main__:Response: [AI-generated poem]

=== Test 2: File Operations with Security ===
INFO:__main__:File operation successful

=== Test 3: Credential Management ===
INFO:__main__:Retrieved credentials successfully

=== Test 4: Tool Recommendations ===
INFO:__main__:Recommended tools: ['language_model', 'file_ops']

=== Test 5: Complex Task ===
INFO:__main__:Analysis: [Tool recommendations for different tasks]

=== Performance Metrics ===
INFO:__main__:Total uses: 2
INFO:__main__:Success rate: 100.00%
INFO:__main__:Average execution time: 1.25s

INFO:__main__:Demo completed successfully!
```

### Customization

You can modify the demo to test different aspects:

1. Change the model:
```python
config = AgentConfig(
    model=ModelType.GPT4O_MINI,  # Try different models
    system_prompt="Your custom prompt",
    temperature=0.9  # Adjust creativity
)
```

2. Add more security rules:
```python
await security.set_tool_permissions(
    "custom_tool",
    {
        PermissionLevel.READ,
        PermissionLevel.EXECUTE,
        PermissionLevel.NETWORK
    }
)
```

3. Test different tasks:
```python
response = await agent.execute(
    "Your custom task description"
)
```

## Other Examples

- (More examples coming soon)
