"""Client implementation for CrewAI adapters with MCP support."""
from contextlib import AsyncExitStack
from types import TracebackType
from typing import Dict, List, Optional, Type, Any, cast
import logging

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import Tool as MCPTool, CallToolResult, TextContent
from pydantic import BaseModel, create_model, Field
from crewai.tools import BaseTool

from crewai_adapters.tools import MCPToolsAdapter, CrewAIToolsAdapter
from crewai_adapters.types import AdapterConfig

class MCPServerConnectionError(Exception):
    """Exception for MCP connection failures."""
    pass

class CrewAIAdapterClient:
    """Client for managing CrewAI adapters and MCP tools."""

    def __init__(self) -> None:
        """Initialize the CrewAI adapter client."""
        self.exit_stack = AsyncExitStack()
        self.sessions: Dict[str, ClientSession] = {}
        self.tools: Dict[str, List[BaseTool]] = {}

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
        """Connect to an MCP server and register its tools.

        Args:
            server_name: Unique identifier for the server connection
            command: Command to start the MCP server
            args: Command line arguments for the server
            env: Optional environment variables
            encoding: Character encoding for communication
            encoding_error_handler: How to handle encoding errors
        """
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
                "parameters": self._convert_tool_schema(tool)
            } for tool in mcp_tools.tools]
        except Exception as e:
            logging.error(f"Failed to get tool configs: {str(e)}")
            return []

    def _convert_tool_schema(self, tool: MCPTool) -> Dict[str, Any]:
        """Convert MCP tool schema to CrewAI compatible format."""
        if not tool.inputSchema:
            return {}

        schema = tool.inputSchema.model_json_schema()
        return {
            "type": "object",
            "properties": schema.get("properties", {}),
            "required": schema.get("required", [])
        }

    async def register_adapter(
        self,
        name: str,
        config: Optional[AdapterConfig] = None
    ) -> None:
        """Register a new native CrewAI adapter.

        Args:
            name: Unique identifier for the adapter
            config: Optional adapter configuration
        """
        adapter = CrewAIToolsAdapter(config)
        self.tools[name] = adapter.get_all_tools()

    def get_tools(self, server_name: Optional[str] = None) -> List[BaseTool]:
        """Get all tools from registered adapters.

        Args:
            server_name: Optional server name to get tools from specific adapter

        Returns:
            List of CrewAI compatible tools
        """
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