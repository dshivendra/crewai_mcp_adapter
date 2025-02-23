"""Client implementation for CrewAI adapters."""
from contextlib import AsyncExitStack
from typing import Dict, List, Optional
from crewai.tools import BaseTool
from crewai_adapters.tools import CrewAIToolsAdapter
from crewai_adapters.types import AdapterConfig

class CrewAIAdapterClient:
    """Client for managing CrewAI adapters and tools."""

    def __init__(self) -> None:
        """Initialize the CrewAI adapter client."""
        self.exit_stack = AsyncExitStack()
        self.adapters: Dict[str, CrewAIToolsAdapter] = {}
        self.adapter_tools: Dict[str, List[BaseTool]] = {}

    async def register_adapter(
        self,
        name: str,
        config: Optional[AdapterConfig] = None
    ) -> None:
        """Register a new adapter with the client.
        
        Args:
            name: Name for the adapter
            config: Optional configuration for the adapter
        """
        adapter = CrewAIToolsAdapter(config)
        self.adapters[name] = adapter
        
        # Load tools from this adapter
        tools = adapter.get_all_tools()
        self.adapter_tools[name] = tools

    def get_tools(self) -> List[BaseTool]:
        """Get all tools from all registered adapters.
        
        Returns:
            List of all available CrewAI tools
        """
        all_tools: List[BaseTool] = []
        for adapter_tools in self.adapter_tools.values():
            all_tools.extend(adapter_tools)
        return all_tools

    async def __aenter__(self) -> "CrewAIAdapterClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.exit_stack.aclose()
