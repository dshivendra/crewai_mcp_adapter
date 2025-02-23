"""
CrewAI Adapters Library
======================

A library providing native adapter support for CrewAI, making it easy to extend and
integrate with various tools and services.
"""

from crewai_adapters.base import BaseAdapter, AdapterRegistry
from crewai_adapters.types import AdapterConfig, AdapterResponse
from crewai_adapters.exceptions import AdapterError

__version__ = "0.1.0"
__all__ = ["BaseAdapter", "AdapterRegistry", "AdapterConfig", "AdapterResponse", "AdapterError"]
