from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import os
import asyncio
import logging
from openai import AsyncOpenAI
from dotenv import load_dotenv

from pydantic import BaseModel

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class ModelType(str, Enum):
    """Supported model types with their specific use cases."""
    GPT35_TURBO = "gpt-3.5-turbo"  # Fast, cost-effective for routine tasks
    GPT4O_MINI = "gpt-4o-mini"     # Multimodal capabilities
    O3_MINI = "o3-mini"            # Advanced reasoning and complex logic
    DALLE = "dall-e"               # Image generation
    WHISPER = "whisper"            # Audio transcription


class AgentConfig(BaseModel):
    """Configuration for an agent instance."""
    model: ModelType
    system_prompt: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    tools_allowed: bool = True
    auto_approve_safe_tools: bool = True


class AgentResponse(BaseModel):
    """Structured response from agent execution."""
    success: bool
    result: Any
    error: Optional[str] = None
    tool_usage: List[Dict[str, Any]] = []
    model_used: ModelType
    tokens_used: Optional[int] = None


class Agent(ABC):
    """Abstract base class for all agents in the framework."""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self._validate_config()
        self.tool_history: List[Dict[str, Any]] = []
        
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        logger.info("Initializing OpenAI client")
        self.client = AsyncOpenAI(api_key=api_key)
    
    @abstractmethod
    async def execute(self, task: str) -> AgentResponse:
        """Execute a task and return the result.
        
        Args:
            task: The task description to execute.
            
        Returns:
            AgentResponse containing execution results and metadata.
        """
        pass
    
    @abstractmethod
    async def discover_tools(self) -> List[Dict[str, Any]]:
        """Discover available tools that can be used by the agent.
        
        Returns:
            List of tool descriptions and capabilities.
        """
        pass
    
    @abstractmethod
    async def request_credentials(self, tool_name: str, required_credentials: List[str]) -> Dict[str, str]:
        """Request necessary credentials from the user.
        
        Args:
            tool_name: Name of the tool requiring credentials.
            required_credentials: List of credential keys needed.
            
        Returns:
            Dictionary of credential key-value pairs.
        """
        pass
    
    def _validate_config(self) -> None:
        """Validate the agent configuration."""
        if self.config.model == ModelType.DALLE and self.config.tools_allowed:
            raise ValueError("DALL-E model does not support tool usage")
        
        if self.config.model == ModelType.WHISPER and self.config.tools_allowed:
            raise ValueError("Whisper model does not support tool usage")


class AutonomousAgent(Agent):
    """Main implementation of an autonomous agent with dynamic tool discovery."""
    
    async def execute(self, task: str) -> AgentResponse:
        """Execute a task using the most appropriate tools and strategies.
        
        This implementation will:
        1. Analyze the task requirements
        2. Discover and select appropriate tools
        3. Request any needed credentials
        4. Execute the task with proper error handling
        5. Learn from the execution for future optimization
        
        Args:
            task: The task description to execute.
            
        Returns:
            AgentResponse containing execution results and metadata.
        """
        try:
            # Create messages for the model
            messages = [
                {"role": "system", "content": self.config.system_prompt},
                {"role": "user", "content": task}
            ]
            
            result = None
            tokens_used = None
            api_error = None
            
            # Call OpenAI API with retries
            for attempt in range(3):  # Maximum 3 retries
                try:
                    logger.info(f"Attempt {attempt + 1} to call OpenAI API")
                    response = await self.client.chat.completions.create(
                        model=self.config.model.value,
                        messages=messages,
                        temperature=self.config.temperature,
                        max_tokens=self.config.max_tokens
                    )
                    
                    # Extract the response
                    if response and response.choices:
                        result = response.choices[0].message.content
                        tokens_used = response.usage.total_tokens if response.usage else None
                        logger.info(f"Successfully got response from OpenAI API")
                        break
                    else:
                        logger.error(f"Empty response from OpenAI API")
                        api_error = "Empty response from API"
                        
                except Exception as e:
                    api_error = str(e)
                    logger.error(f"API call failed on attempt {attempt + 1}: {api_error}")
                    logger.error(f"API key length: {len(os.getenv('OPENAI_API_KEY', ''))}")
                    if attempt == 2:  # Last attempt
                        break
                    # Exponential backoff
                    await asyncio.sleep(2 ** attempt)  # 1s, 2s, 4s
            
            if result is None:
                error_msg = f"Failed to get response from OpenAI API after 3 attempts: {api_error}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # Record tool usage
            self.tool_history.append({
                "tool": "openai_api",
                "task": task,
                "success": True,
                "tokens": tokens_used
            })
            
            return AgentResponse(
                success=True,
                result=result,
                model_used=self.config.model,
                tool_usage=self.tool_history,
                tokens_used=tokens_used
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                result=None,
                error=str(e),
                model_used=self.config.model,
                tool_usage=self.tool_history
            )
    
    async def discover_tools(self) -> List[Dict[str, Any]]:
        """Discover available tools through system scanning.
        
        This implementation will:
        1. Scan system for available commands
        2. Check for installed packages
        3. Identify available APIs
        4. Parse tool documentation
        
        Returns:
            List of discovered tools with their capabilities.
        """
        # TODO: Implement tool discovery logic
        return []
    
    async def request_credentials(self, tool_name: str, required_credentials: List[str]) -> Dict[str, str]:
        """Request necessary credentials from the user.
        
        Args:
            tool_name: Name of the tool requiring credentials.
            required_credentials: List of credential keys needed.
            
        Returns:
            Dictionary of credential key-value pairs.
        """
        # TODO: Implement secure credential request system
        return {}
