"""Test fixtures and helper classes for testing."""
from typing import Any, Dict, List
from crewai_adapters.base import BaseAdapter
from crewai_adapters.types import AdapterResponse, AdapterConfig
from crewai_adapters.tools import CrewAITool
from mcp.types import Tool as MCPTool, CallToolResult, TextContent
from langchain_core.tools import BaseTool

class MockAdapter(BaseAdapter):
    """Mock adapter implementation for testing."""

    def _validate_config(self) -> None:
        """Validate configuration."""
        pass

    async def execute(self, **kwargs) -> AdapterResponse:
        """Execute test functionality."""
        return AdapterResponse(success=True, data="test")

class MockMCPTool(MCPTool):
    """Mock MCP tool for testing."""

    async def execute(self, parameters: Dict[str, Any]) -> CallToolResult:
        """Execute mock tool."""
        content = [TextContent(text="mock_result")]
        return CallToolResult(content=content, isError=False)

def create_mock_mcp_tool() -> MCPTool:
    """Create a mock MCP tool."""
    return MockMCPTool(
        name="mock_mcp_tool",
        description="Mock MCP tool for testing",
        inputSchema={"test": {"type": "string"}}
    )

def create_mock_crewai_tool() -> CrewAITool:
    """Create a mock CrewAI tool."""
    async def mock_execute(**kwargs: Any) -> str:
        return "mock_result"

    return CrewAITool(
        name="mock_crewai_tool",
        description="Mock CrewAI tool for testing",
        parameters={"test": {"type": "string"}},
        func=mock_execute
    )