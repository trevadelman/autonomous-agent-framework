"""
Autonomous Agent Framework
-------------------------

A flexible Python framework for creating autonomous agents that can discover,
learn, and utilize tools dynamically to accomplish tasks.
"""

from autonomous_agent_framework.core.agent import (
    Agent,
    AutonomousAgent,
    AgentConfig,
    AgentResponse,
    ModelType
)
from autonomous_agent_framework.tools.discovery import (
    ToolDiscovery,
    ToolCategory,
    ToolCapability,
    ToolMetadata
)
from autonomous_agent_framework.core.credentials import CredentialManager

__version__ = "0.1.0"
__all__ = [
    "Agent",
    "AutonomousAgent",
    "AgentConfig",
    "AgentResponse",
    "ModelType",
    "ToolDiscovery",
    "ToolCategory",
    "ToolCapability",
    "ToolMetadata",
    "CredentialManager"
]
