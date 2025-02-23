"""Tests for MCP adapter implementation."""
import pytest
from crewai.tools import BaseTool
from crewai_adapters.tools import MCPToolsAdapter
from crewai_adapters.exceptions import ConfigurationError
from crewai_adapters.types import AdapterConfig, AdapterResponse
from tests.fixtures import create_mock_mcp_tool, MockTool

@pytest.mark.asyncio
class TestMCPToolsAdapter:
    """Test suite for MCPToolsAdapter."""

    async def test_successful_execution(self):
        """Test successful adapter execution."""
        mock_tool = create_mock_mcp_tool()
        adapter = MCPToolsAdapter(AdapterConfig({
            "tools": [{
                "name": mock_tool.name,
                "description": mock_tool.description,
                "parameters": mock_tool.inputSchema
            }]
        }))

        response = await adapter.execute(
            tool_name=mock_tool.name,
            parameters={"test": "value"}
        )
        assert response.success
        assert isinstance(response.data, str)
        assert response.metadata is not None
        assert response.metadata["source"] == "MCPToolsAdapter"

    async def test_missing_config(self):
        """Test adapter behavior with missing configuration."""
        with pytest.raises(ConfigurationError):
            adapter = MCPToolsAdapter(AdapterConfig({}))
            await adapter.execute()

    async def test_missing_tool(self):
        """Test adapter with non-existent tool."""
        adapter = MCPToolsAdapter(AdapterConfig({
            "tools": [{
                "name": "test_tool",
                "description": "Test tool",
                "parameters": {}
            }]
        }))

        response = await adapter.execute(tool_name="non_existent")
        assert not response.success
        assert "Tool non_existent not found" == response.error

    async def test_tool_conversion(self):
        """Test conversion to CrewAI tool."""
        mock_tool = create_mock_mcp_tool()
        adapter = MCPToolsAdapter(AdapterConfig({
            "tools": [{
                "name": mock_tool.name,
                "description": mock_tool.description,
                "parameters": mock_tool.inputSchema
            }]
        }))

        tools = adapter.get_all_tools()
        assert len(tools) == 1
        assert isinstance(tools[0], BaseTool)
        assert tools[0].name == mock_tool.name
        assert tools[0].description == mock_tool.description

    async def test_metadata_structure(self):
        """Test metadata in response."""
        mock_tool = create_mock_mcp_tool()
        adapter = MCPToolsAdapter(AdapterConfig({
            "tools": [{
                "name": mock_tool.name,
                "description": mock_tool.description,
                "parameters": mock_tool.inputSchema
            }]
        }))

        response = await adapter.execute(
            tool_name=mock_tool.name,
            parameters={"test": "value"}
        )
        assert response.metadata is not None
        assert "timestamp" in response.metadata
        assert "duration" in response.metadata
        assert "source" in response.metadata
        assert response.metadata["source"] == "MCPToolsAdapter"