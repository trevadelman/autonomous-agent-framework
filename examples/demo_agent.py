import asyncio
import logging
import os
from pathlib import Path
from datetime import datetime, UTC
from dotenv import load_dotenv

from autonomous_agent_framework import (
    AutonomousAgent,
    AgentConfig,
    ModelType
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Verify OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")
logger.info(f"OpenAI API key loaded (length: {len(api_key)})")
from autonomous_agent_framework.core.credentials import CredentialManager
from autonomous_agent_framework.core.learning import LearningSystem, ToolUsageMetrics
from autonomous_agent_framework.core.security import (
    ToolSecurity,
    PermissionLevel,
    ResourceLimit
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def setup_security():
    """Set up security configuration for tools."""
    security = ToolSecurity()
    
    # Set up permissions for file operations
    await security.set_tool_permissions(
        "file_ops",
        {
            PermissionLevel.READ,
            PermissionLevel.WRITE
        }
    )
    
    # Set up resource limits
    await security.set_resource_limits(
        "file_ops",
        ResourceLimit(
            max_file_size_mb=10,
            max_execution_time_sec=5
        )
    )
    
    return security

async def setup_credentials():
    """Set up credential management."""
    cred_manager = CredentialManager(app_name="demo_agent")
    
    # Example of storing and retrieving credentials
    test_creds = {
        "api_key": "test_key",
        "secret": "test_secret"
    }
    
    await cred_manager.store_credentials(
        "test_api",
        test_creds,
        require_confirmation=False
    )
    
    return cred_manager

async def main():
    try:
        # Initialize components
        security = await setup_security()
        cred_manager = await setup_credentials()
        learning = LearningSystem()
        
        # Create agent configuration
        config = AgentConfig(
            model=ModelType.GPT35_TURBO,
            system_prompt=(
                "You are a helpful assistant that can perform various tasks "
                "using available tools. You should be creative and efficient "
                "in your solutions."
            ),
            temperature=0.7
        )
        
        # Initialize agent
        agent = AutonomousAgent(config)
        logger.info("Agent initialized successfully")
        
        # Test 1: Basic Task
        logger.info("\n=== Test 1: Basic Task ===")
        response = await agent.execute(
            "Create a short poem about artificial intelligence and tools."
        )
        logger.info(f"Response: {response.result}")
        
        # Record successful tool usage with estimated execution time
        await learning.record_tool_usage(ToolUsageMetrics(
            tool_name="language_model",
            success=response.success,
            execution_time=0.5,  # Estimated time
            context={"task": "creative_writing"},
            output_result={"response": response.result}
        ))
        
        # Add delay between tasks
        await asyncio.sleep(1)

        # Test 2: File Operations with Security
        logger.info("\n=== Test 2: File Operations with Security ===")
        # Validate tool usage
        can_use_files = await security.validate_tool_usage(
            "file_ops",
            {PermissionLevel.WRITE},
            resource_usage={"file_size_mb": 1}
        )
        
        if can_use_files:
            test_file = Path("test_output.txt")
            test_file.write_text("This is a test file created by the demo agent.")
            logger.info("File operation successful")
            
            # Record file operation
            await learning.record_tool_usage(ToolUsageMetrics(
                tool_name="file_ops",
                success=True,
                execution_time=0.1,
                context={"operation": "write"}
            ))
            
            # Cleanup
            test_file.unlink()
        
        # Test 3: Credential Management
        logger.info("\n=== Test 3: Credential Management ===")
        creds = await cred_manager.get_credentials(
            "test_api",
            required_keys=["api_key", "secret"]
        )
        logger.info("Retrieved credentials successfully")
        
        # Test 4: Tool Recommendations
        logger.info("\n=== Test 4: Tool Recommendations ===")
        recommendations = await learning.get_tool_recommendations(
            context={"task": "creative_writing"}
        )
        logger.info(f"Recommended tools: {recommendations}")
        
        # Add delay between tasks
        await asyncio.sleep(1)

        # Test 5: Complex Task
        logger.info("\n=== Test 5: Complex Task ===")
        try:
            response = await agent.execute(
                "Analyze the following tasks and suggest the best tools for each:\n"
                "1. Writing a report\n"
                "2. Processing image data\n"
                "3. Making API calls\n"
                "4. File management"
            )
            logger.info(f"Analysis: {response.result}")
            
            # Record complex task usage
            await learning.record_tool_usage(ToolUsageMetrics(
                tool_name="language_model",
                success=response.success,
                execution_time=0.8,  # Estimated time
                context={"task": "task_analysis"},
                output_result={"response": response.result}
            ))
        except Exception as e:
            logger.error(f"Error in complex task: {str(e)}")
        
        # Get performance metrics
        logger.info("\n=== Performance Metrics ===")
        perf = await learning.get_tool_performance("language_model")
        if perf:
            logger.info(f"Total uses: {perf.total_uses}")
            logger.info(f"Success rate: {perf.successful_uses/perf.total_uses:.2%}")
            logger.info(f"Average execution time: {perf.average_execution_time:.2f}s")
        
        logger.info("\nDemo completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during demo: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())
