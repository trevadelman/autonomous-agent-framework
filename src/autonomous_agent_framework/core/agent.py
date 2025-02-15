from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel


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
            # TODO: Implement core execution logic
            # This will be expanded as we implement the tool discovery
            # and execution systems
            
            return AgentResponse(
                success=True,
                result="Task execution not yet implemented",
                model_used=self.config.model,
                tool_usage=[]
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
