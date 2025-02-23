"""Test fixtures and helper classes for testing."""
from crewai_adapters.base import BaseAdapter
from crewai_adapters.types import AdapterResponse

class MockAdapter(BaseAdapter):
    """Mock adapter implementation for testing."""
    
    def _validate_config(self) -> None:
        """Validate configuration."""
        pass
        
    async def execute(self, **kwargs) -> AdapterResponse:
        """Execute test functionality."""
        return AdapterResponse(success=True, data="test")
