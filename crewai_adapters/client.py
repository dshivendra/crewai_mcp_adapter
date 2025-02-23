"""Client implementation for CrewAI adapters."""
from contextlib import AsyncExitStack
from types import TracebackType
from typing import Dict, List, Optional, Type, Union, cast, Any
import logging
from crewai.tools import BaseTool as Tool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import Tool as MCPTool, CallToolResult, TextContent
from pydantic import BaseModel, create_model, Field

from crewai_adapters.tools import MCPToolsAdapter, CrewAIToolsAdapter
from crewai_adapters.types import AdapterConfig

class MCPServerConnectionError(Exception):
    """Exception for MCP connection failures."""
    pass

class CrewAIAdapterClient:
    """Client for managing CrewAI adapters and tools."""

    def __init__(self) -> None:
        """Initialize the CrewAI adapter client."""
        self.exit_stack = AsyncExitStack()
        self.sessions: Dict[str, ClientSession] = {}
        self.tools: Dict[str, List[Tool]] = {}

    async def connect_to_mcp_server(
        self,
        server_name: str,
        *,
        command: str,
        args: List[str],
        env: Optional[Dict[str, str]] = None,
        encoding: str = "utf-8",
        encoding_error_handler: str = "strict"
    ) -> None:
        """Connect to an MCP server and register its tools."""
        try:
            server_params = StdioServerParameters(
                command=command,
                args=args,
                env=env,
                encoding=encoding,
                encoding_error_handler=encoding_error_handler
            )

            transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read, write = transport
            session = cast(
                ClientSession,
                await self.exit_stack.enter_async_context(ClientSession(read, write))
            )

            await session.initialize()
            self.sessions[server_name] = session

            # Create adapter and load tools
            adapter = MCPToolsAdapter(AdapterConfig({
                "tools": await self._get_mcp_tool_configs(session)
            }))
            self.tools[server_name] = adapter.get_all_tools()

        except Exception as e:
            logging.error(f"Connection failed: {str(e)}")
            raise MCPServerConnectionError(f"Failed to connect to {server_name}") from e

    async def _get_mcp_tool_configs(self, session: ClientSession) -> List[Dict[str, Any]]:
        """Get tool configurations from MCP server."""
        try:
            mcp_tools = await session.list_tools()
            return [{
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            } for tool in mcp_tools.tools]
        except Exception as e:
            logging.error(f"Failed to get tool configs: {str(e)}")
            return []

    async def register_adapter(
        self,
        name: str,
        config: Optional[AdapterConfig] = None
    ) -> None:
        """Register a new native CrewAI adapter."""
        adapter = CrewAIToolsAdapter(config)
        self.tools[name] = adapter.get_all_tools()

    def get_tools(self, server_name: Optional[str] = None) -> List[Tool]:
        """Get all tools from registered adapters."""
        if server_name:
            return self.tools.get(server_name, [])
        return [tool for tools in self.tools.values() for tool in tools]

    async def __aenter__(self) -> "CrewAIAdapterClient":
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> None:
        """Async context manager exit."""
        await self.exit_stack.aclose()