"""
CrewAI Adapters Library
======================

A library providing native adapter support for CrewAI using adapter patterns.
"""

from crewai_adapters.base import BaseAdapter, AdapterRegistry
from crewai_adapters.types import AdapterConfig, AdapterResponse
from crewai_adapters.exceptions import AdapterError
from crewai_adapters.tools import CrewAIToolsAdapter, CrewAITool
from crewai_adapters.client import CrewAIAdapterClient

__version__ = "0.1.0"
__all__ = [
    "BaseAdapter",
    "AdapterRegistry",
    "AdapterConfig",
    "AdapterResponse",
    "AdapterError",
    "CrewAIToolsAdapter",
    "CrewAITool",
    "CrewAIAdapterClient"
]