import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from autonomous_agent_framework.tools.discovery import (
    ToolDiscovery,
    ToolCategory,
    ToolCapability,
    ToolMetadata
)

@pytest.fixture
def tool_discovery():
    return ToolDiscovery()

@pytest.fixture
def mock_env_vars():
    with patch.dict(os.environ, {
        "OPENAI_API_KEY": "dummy_key",
        "GITHUB_TOKEN": "dummy_token",
        "AWS_ACCESS_KEY": "dummy_access"
    }):
        yield

@pytest.fixture
def mock_cli_tools():
    def mock_which(tool):
        # Simulate git and npm being installed
        return str(Path("/usr/bin") / tool) if tool in ["git", "npm"] else None
    
    with patch("shutil.which", side_effect=mock_which):
        yield

class TestToolDiscovery:
    @pytest.mark.asyncio
    async def test_discover_apis(self, tool_discovery, mock_env_vars):
        """Test API discovery from environment variables."""
        await tool_discovery._discover_apis()
        
        tools = tool_discovery._discovered_tools
        
        # Check if APIs were discovered from env vars
        assert "openai_api" in tools
        assert "github_api" in tools
        assert "aws_api" in tools
        
        # Verify API tool metadata
        openai_tool = tools["openai_api"]
        assert openai_tool.category == ToolCategory.API
        assert ToolCapability.API_CALL in openai_tool.capabilities
        assert openai_tool.requires_credentials
        assert "OPENAI_API_KEY" in openai_tool.required_credentials

    @pytest.mark.asyncio
    async def test_discover_cli_tools(self, tool_discovery, mock_cli_tools):
        """Test CLI tool discovery."""
        # Mock the version and help text responses
        async def mock_run_command(command):
            if command[1] == "--version":
                return "2.34.1"
            elif command[1] == "--help":
                return "Git - distributed version control system\nUsage: git [options]"
            return ""
        
        with patch.object(tool_discovery, "_run_command", side_effect=mock_run_command):
            await tool_discovery._discover_cli_tools()
        
        tools = tool_discovery._discovered_tools
        
        # Check if git was discovered
        assert "git" in tools
        git_tool = tools["git"]
        
        # Verify git tool metadata
        assert git_tool.category == ToolCategory.CLI
        assert git_tool.version == "2.34.1"
        assert "distributed version control system" in git_tool.description.lower()

    @pytest.mark.asyncio
    async def test_discover_file_operations(self, tool_discovery):
        """Test file operations discovery."""
        await tool_discovery._discover_file_operations()
        
        tools = tool_discovery._discovered_tools
        
        # Check if file operations were discovered
        assert "file_ops" in tools
        file_ops = tools["file_ops"]
        
        # Verify file operations metadata
        assert file_ops.category == ToolCategory.FILE_OPERATION
        assert ToolCapability.FILE_READ in file_ops.capabilities
        assert ToolCapability.FILE_WRITE in file_ops.capabilities

    @pytest.mark.asyncio
    async def test_discover_all(self, tool_discovery, mock_env_vars, mock_cli_tools):
        """Test complete tool discovery process."""
        # Mock the version and help text responses
        async def mock_run_command(command):
            if command[1] == "--version":
                return "2.34.1"
            elif command[1] == "--help":
                return "Git - distributed version control system\nUsage: git [options]"
            return ""
        
        with patch.object(tool_discovery, "_run_command", side_effect=mock_run_command):
            tools = await tool_discovery.discover_all()
        
        # Convert tools to a dict for easier testing
        tools_dict = {tool["name"]: tool for tool in tools}
        
        # Verify we discovered tools from all categories
        assert "git" in tools_dict  # CLI tool
        assert "openai_api" in tools_dict  # API
        assert "file_ops" in tools_dict  # File operations
        
        # Verify tool details
        git_tool = tools_dict["git"]
        assert git_tool["category"] == ToolCategory.CLI
        assert git_tool["version"] == "2.34.1"
        
        openai_tool = tools_dict["openai_api"]
        assert openai_tool["category"] == ToolCategory.API
        assert openai_tool["requires_credentials"]
        
        file_ops = tools_dict["file_ops"]
        assert file_ops["category"] == ToolCategory.FILE_OPERATION
        assert ToolCapability.FILE_READ in file_ops["capabilities"]
