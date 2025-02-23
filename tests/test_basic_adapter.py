"""Tests for basic adapter implementation."""
import pytest
from crewai_adapters.adapters.basic import BasicAdapter
from crewai_adapters.exceptions import ConfigurationError
from crewai_adapters.types import AdapterConfig, AdapterResponse

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
        assert "timestamp" in response.metadata
        assert "duration" in response.metadata
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

    async def test_metadata_structure(self):
        """Test metadata structure in response."""
        adapter = BasicAdapter(AdapterConfig({"name": "TestAdapter"}))

        response = await adapter.execute()
        assert response.metadata is not None
        assert isinstance(response.metadata["timestamp"], str)
        assert isinstance(response.metadata["duration"], float)
        assert response.metadata["source"] == "BasicAdapter"

    async def test_additional_parameters(self):
        """Test adapter with additional parameters."""
        adapter = BasicAdapter(AdapterConfig({"name": "TestAdapter"}))

        response = await adapter.execute(
            message="Test",
            additional_param="ignored"
        )
        assert response.success
        assert response.data == "TestAdapter: Test"