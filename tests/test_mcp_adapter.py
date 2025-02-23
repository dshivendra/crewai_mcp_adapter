"""Tests for MCP adapter implementation."""
import pytest
from crewai_adapters.tools import MCPToolsAdapter
from crewai_adapters.exceptions import ConfigurationError
from crewai_adapters.types import AdapterConfig, AdapterResponse
from tests.fixtures import create_mock_mcp_tool

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
        assert response.data == "mock_result"
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
        assert isinstance(response.metadata["timestamp"], str)
        assert isinstance(response.metadata["duration"], float)
        assert response.metadata["source"] == "MCPToolsAdapter"