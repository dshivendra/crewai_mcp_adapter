"""Tests for basic adapter implementation."""
import pytest
from crewai.tools import BaseTool
from crewai_adapters.adapters.basic import BasicAdapter
from crewai_adapters.tools import CrewAIToolsAdapter
from crewai_adapters.exceptions import ConfigurationError
from crewai_adapters.types import AdapterConfig, AdapterResponse
from tests.fixtures import create_mock_crewai_tool

@pytest.mark.asyncio
class TestBasicAdapter:
    """Test suite for BasicAdapter."""

    async def test_successful_execution(self):
        """Test successful adapter execution."""
        adapter = BasicAdapter(AdapterConfig({"name": "TestAdapter"}))

        response = await adapter.execute(message="Test message")
        assert response.success
        assert response.data == "TestAdapter: Test message"
        assert response.metadata is not None
        assert isinstance(response.metadata["timestamp"], str)
        assert isinstance(response.metadata["duration"], float)
        assert response.metadata["source"] == "BasicAdapter"

    async def test_missing_config(self):
        """Test adapter behavior with missing configuration."""
        with pytest.raises(ConfigurationError):
            adapter = BasicAdapter(AdapterConfig({}))
            await adapter.execute()

    async def test_default_message(self):
        """Test adapter with default message."""
        adapter = BasicAdapter(AdapterConfig({"name": "TestAdapter"}))

        response = await adapter.execute()
        assert response.success
        assert response.data == "TestAdapter: Hello from BasicAdapter!"

@pytest.mark.asyncio
class TestCrewAIToolsAdapter:
    """Test suite for CrewAIToolsAdapter."""

    async def test_successful_execution(self):
        """Test successful adapter execution."""
        mock_tool = await create_mock_crewai_tool()
        adapter = CrewAIToolsAdapter(AdapterConfig({
            "tools": [{
                "name": mock_tool.name,
                "description": mock_tool.description,
                "parameters": mock_tool.parameters,
                "func": mock_tool.func
            }]
        }))

        response = await adapter.execute(
            tool_name=mock_tool.name,
            parameters={"test": "value"}
        )
        assert response.success
        assert response.data == "mock_result: value"
        assert response.metadata is not None
        assert response.metadata["source"] == "CrewAIToolsAdapter"

    async def test_missing_config(self):
        """Test adapter behavior with missing configuration."""
        with pytest.raises(ConfigurationError):
            adapter = CrewAIToolsAdapter(AdapterConfig({}))
            await adapter.execute()

    async def test_missing_tool(self):
        """Test adapter with non-existent tool."""
        adapter = CrewAIToolsAdapter(AdapterConfig({
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
        mock_tool = await create_mock_crewai_tool()
        adapter = CrewAIToolsAdapter(AdapterConfig({
            "tools": [{
                "name": mock_tool.name,
                "description": mock_tool.description,
                "parameters": mock_tool.parameters,
                "func": mock_tool.func
            }]
        }))

        tools = adapter.get_all_tools()
        assert len(tools) == 1
        assert isinstance(tools[0], BaseTool)
        assert tools[0].name == mock_tool.name
        assert tools[0].description == mock_tool.description

    async def test_metadata_structure(self):
        """Test metadata in response."""
        mock_tool = await create_mock_crewai_tool()
        adapter = CrewAIToolsAdapter(AdapterConfig({
            "tools": [{
                "name": mock_tool.name,
                "description": mock_tool.description,
                "parameters": mock_tool.parameters,
                "func": mock_tool.func
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
        assert response.metadata["source"] == "CrewAIToolsAdapter"