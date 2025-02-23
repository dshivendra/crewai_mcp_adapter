"""Test fixtures and helper classes for testing."""
from typing import Any, Dict, List
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from crewai_adapters.base import BaseAdapter
from crewai_adapters.types import AdapterResponse, AdapterConfig
from crewai_adapters.tools import CrewAITool
from mcp.types import Tool as MCPTool

class MockToolInput(BaseModel):
    """Input schema for mock tool."""
    test: str = Field(..., description="Test parameter")

class MockTool(BaseTool):
    """Mock tool for testing."""
    name: str = "mock_tool"
    description: str = "Mock tool for testing"
    args_schema: type[BaseModel] = MockToolInput

    async def _run(self, test: str) -> str:
        """Execute the mock tool."""
        return f"mock_result: {test}"

class MockAdapter(BaseAdapter):
    """Mock adapter implementation for testing."""

    def _validate_config(self) -> None:
        """Validate configuration."""
        pass

    async def execute(self, **kwargs) -> AdapterResponse:
        """Execute test functionality."""
        return AdapterResponse(success=True, data="test")

async def create_mock_crewai_tool() -> CrewAITool:
    """Create a mock CrewAI tool."""
    async def mock_execute(test: str) -> str:
        return f"mock_result: {test}"

    return CrewAITool(
        name="mock_crewai_tool",
        description="Mock CrewAI tool for testing",
        parameters=MockToolInput.model_json_schema(),
        func=mock_execute
    )

def create_mock_mcp_tool() -> MCPTool:
    """Create a mock MCP tool."""
    return MCPTool(
        name="mock_mcp_tool",
        description="Mock MCP tool for testing",
        inputSchema=MockToolInput.model_json_schema()
    )