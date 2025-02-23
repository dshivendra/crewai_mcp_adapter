"""Context protocol client implementation for CrewAI adapters."""
from typing import Any, Dict, List, Optional, Sequence
from mcp import MCPClient
from mcp.config import Config as MCPConfig
from crewai_adapters.types import AdapterResponse, AdapterConfig
from crewai_adapters.utils import create_metadata

class MCPCrewClient:
    """Client for Model Context Protocol."""

    def __init__(
        self,
        client: Optional[MCPClient] = None,
        config: Optional[MCPConfig] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize MCP client."""
        self.client = client or MCPClient(config=config, **kwargs)

    async def get_context(
        self,
        messages: Sequence[Dict[str, Any]],
        *,
        include_system_messages: bool = True,
        **kwargs: Any,
    ) -> str:
        """Get context string from messages."""
        return await self.client.get_context(
            messages=messages,
            include_system_messages=include_system_messages,
            **kwargs
        )

    async def extract_valid_context(
        self,
        messages: Sequence[Dict[str, Any]],
        *,
        include_system_messages: bool = True,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """Extract valid context from messages."""
        return await self.client.extract_valid_context(
            messages=messages,
            include_system_messages=include_system_messages,
            **kwargs
        )

    async def execute(self, messages: Sequence[Dict[str, Any]], start_time: Optional[Any] = None, **kwargs) -> AdapterResponse:
        try:
            processed_context = await self.extract_valid_context(messages, **kwargs)
            metadata = create_metadata(
                source=self.__class__.__name__,
                start_time=start_time,
                additional_data={"model": "MCP Model"} # Placeholder - needs actual model name
            )
            return AdapterResponse(
                success=True,
                data=processed_context,
                metadata=metadata
            )
        except Exception as e:
            return AdapterResponse(
                success=False,
                error=str(e)
            )