import os
import subprocess
from typing import Any, Dict, List, Optional, Set
from importlib.metadata import distributions, Distribution
import shutil
from pathlib import Path

class ToolCategory:
    """Categories of discoverable tools."""
    CLI = "cli"
    PYTHON_PACKAGE = "python_package"
    API = "api"
    FILE_OPERATION = "file_operation"
    SYSTEM = "system"


class ToolCapability:
    """Standard capabilities that tools might provide."""
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    NETWORK = "network"
    PROCESS = "process"
    DATABASE = "database"
    API_CALL = "api_call"


class ToolMetadata:
    """Metadata about a discovered tool."""
    def __init__(
        self,
        name: str,
        category: str,
        capabilities: Set[str],
        description: str,
        requires_credentials: bool = False,
        required_credentials: Optional[List[str]] = None,
        version: Optional[str] = None,
        documentation_url: Optional[str] = None
    ):
        self.name = name
        self.category = category
        self.capabilities = capabilities
        self.description = description
        self.requires_credentials = requires_credentials
        self.required_credentials = required_credentials or []
        self.version = version
        self.documentation_url = documentation_url

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary format."""
        return {
            "name": self.name,
            "category": self.category,
            "capabilities": list(self.capabilities),
            "description": self.description,
            "requires_credentials": self.requires_credentials,
            "required_credentials": self.required_credentials,
            "version": self.version,
            "documentation_url": self.documentation_url
        }


class ToolDiscovery:
    """System tool discovery and analysis."""

    def __init__(self):
        self._discovered_tools: Dict[str, ToolMetadata] = {}
        self._common_cli_tools = {
            "git", "npm", "python", "pip", "node",
            "docker", "kubectl", "aws", "gcloud"
        }

    async def discover_all(self) -> List[Dict[str, Any]]:
        """Discover all available tools across categories.
        
        Returns:
            List of tool metadata dictionaries.
        """
        await self._discover_cli_tools()
        await self._discover_python_packages()
        await self._discover_apis()
        await self._discover_file_operations()
        
        return [tool.to_dict() for tool in self._discovered_tools.values()]

    async def _discover_cli_tools(self) -> None:
        """Discover available CLI tools and their capabilities."""
        for tool in self._common_cli_tools:
            path = shutil.which(tool)
            if path:
                try:
                    # Get version and help info
                    version = await self._get_cli_version(tool)
                    help_text = await self._get_cli_help(tool)
                    
                    capabilities = set()
                    if any(kw in help_text.lower() for kw in ["file", "read", "write"]):
                        capabilities.update([ToolCapability.FILE_READ, ToolCapability.FILE_WRITE])
                    if any(kw in help_text.lower() for kw in ["http", "api", "request"]):
                        capabilities.add(ToolCapability.NETWORK)
                    
                    self._discovered_tools[tool] = ToolMetadata(
                        name=tool,
                        category=ToolCategory.CLI,
                        capabilities=capabilities,
                        description=self._extract_description(help_text),
                        version=version
                    )
                except Exception:
                    # Skip tools that can't be analyzed
                    continue

    async def _discover_python_packages(self) -> None:
        """Discover installed Python packages and their capabilities."""
        for dist in distributions():
            try:
                metadata = dist.metadata
                capabilities = set()
                
                # Analyze package metadata for capabilities
                metadata_text = str(metadata).lower()
                if any(kw in metadata_text for kw in ["file", "io", "read", "write"]):
                    capabilities.update([ToolCapability.FILE_READ, ToolCapability.FILE_WRITE])
                if any(kw in metadata_text for kw in ["http", "api", "request"]):
                    capabilities.add(ToolCapability.NETWORK)
                if any(kw in metadata_text for kw in ["sql", "database", "db"]):
                    capabilities.add(ToolCapability.DATABASE)
                
                self._discovered_tools[dist.name] = ToolMetadata(
                    name=dist.name,
                    category=ToolCategory.PYTHON_PACKAGE,
                    capabilities=capabilities,
                    description=metadata.get("Summary", "No description available"),
                    version=dist.version
                )
            except Exception:
                # Skip packages that can't be analyzed
                continue

    async def _discover_apis(self) -> None:
        """Discover available APIs through configuration and environment."""
        # Check environment variables for API configurations
        for env_var in os.environ:
            if any(kw in env_var.lower() for kw in ["api", "token", "key"]):
                service_name = env_var.split("_")[0].lower()
                self._discovered_tools[f"{service_name}_api"] = ToolMetadata(
                    name=f"{service_name}_api",
                    category=ToolCategory.API,
                    capabilities={ToolCapability.API_CALL, ToolCapability.NETWORK},
                    description=f"API access for {service_name}",
                    requires_credentials=True,
                    required_credentials=[env_var]
                )

    async def _discover_file_operations(self) -> None:
        """Discover available file operation capabilities."""
        # Basic file operations are always available
        self._discovered_tools["file_ops"] = ToolMetadata(
            name="file_ops",
            category=ToolCategory.FILE_OPERATION,
            capabilities={ToolCapability.FILE_READ, ToolCapability.FILE_WRITE},
            description="Basic file system operations"
        )

    async def _get_cli_version(self, tool: str) -> Optional[str]:
        """Get version information for a CLI tool."""
        try:
            result = await self._run_command([tool, "--version"])
            return result.strip()
        except Exception:
            return None

    async def _get_cli_help(self, tool: str) -> str:
        """Get help text for a CLI tool."""
        try:
            result = await self._run_command([tool, "--help"])
            return result
        except Exception:
            return ""

    async def _run_command(self, command: List[str]) -> str:
        """Run a command and return its output."""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout
        except subprocess.TimeoutExpired:
            return ""

    def _extract_description(self, help_text: str) -> str:
        """Extract a brief description from help text."""
        # Take first non-empty line as description
        lines = [line.strip() for line in help_text.split("\n")]
        for line in lines:
            if line and not line.startswith("-"):
                return line
        return "No description available"
