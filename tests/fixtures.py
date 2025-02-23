"""Test fixtures and helper classes for testing."""
from typing import Any, Dict, List
from crewai.tools import Tool
from crewai_adapters.base import BaseAdapter
from crewai_adapters.types import AdapterResponse, AdapterConfig
from crewai_adapters.tools import CrewAITool

class MockAdapter(BaseAdapter):
    """Mock adapter implementation for testing."""

    def _validate_config(self) -> None:
        """Validate configuration."""
        pass

    async def execute(self, **kwargs) -> AdapterResponse:
        """Execute test functionality."""
        return AdapterResponse(success=True, data="test")

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