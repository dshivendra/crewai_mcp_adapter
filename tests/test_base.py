"""Tests for base adapter functionality."""
import pytest
from tests.fixtures import MockAdapter
from crewai.tools import BaseTool
from crewai_adapters.base import BaseAdapter, AdapterRegistry
from crewai_adapters.types import AdapterConfig, AdapterResponse
from crewai_adapters.exceptions import AdapterError, ConfigurationError

def test_adapter_registry():
    """Test adapter registry functionality."""
    # Clear registry
    AdapterRegistry._adapters = {}

    # Test registration
    AdapterRegistry.register("test", MockAdapter)
    assert "test" in AdapterRegistry._adapters

    # Test retrieval
    adapter_cls = AdapterRegistry.get("test")
    assert adapter_cls == MockAdapter

    # Test duplicate registration
    with pytest.raises(AdapterError):
        AdapterRegistry.register("test", MockAdapter)

    # Test getting non-existent adapter
    with pytest.raises(AdapterError):
        AdapterRegistry.get("non_existent")

    # Test listing adapters
    adapters = AdapterRegistry.list_adapters()
    assert "test" in adapters
    assert len(adapters) == 1

@pytest.mark.asyncio
async def test_base_adapter():
    """Test base adapter functionality."""
    config = AdapterConfig({"test": "value"})
    adapter = MockAdapter(config)

    assert adapter.config == config

    response = await adapter.execute()
    assert response.success
    assert response.data == "test"

@pytest.mark.asyncio
async def test_adapter_creation():
    """Test adapter creation with kwargs."""
    adapter = MockAdapter.create(test="value")
    assert isinstance(adapter.config, AdapterConfig)
    assert adapter.config["test"] == "value"

    response = await adapter.execute()
    assert response.success
    assert response.data == "test"