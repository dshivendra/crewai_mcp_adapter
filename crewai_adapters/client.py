"""Client implementation for CrewAI adapters."""
from contextlib import AsyncExitStack
from types import TracebackType
from typing import Dict, List, Optional, Type, Union
from langchain_core.tools import BaseTool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from crewai_adapters.tools import MCPToolsAdapter, CrewAIToolsAdapter
from crewai_adapters.types import AdapterConfig

class CrewAIAdapterClient:
    """Client for managing CrewAI adapters and tools."""

    def __init__(self) -> None:
        """Initialize the CrewAI adapter client."""
        self.exit_stack = AsyncExitStack()
        self.sessions: Dict[str, ClientSession] = {}
        self.adapters: Dict[str, Union[MCPToolsAdapter, CrewAIToolsAdapter]] = {}
        self.adapter_tools: Dict[str, List[BaseTool]] = {}

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
            server_name: Name to identify the server
            command: Command to start the server
            args: Command arguments
            env: Optional environment variables
            encoding: Server output encoding
            encoding_error_handler: How to handle encoding errors
        """
        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=env,
            encoding=encoding,
            encoding_error_handler=encoding_error_handler
        )

        # Create and store the connection
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        read, write = stdio_transport
        session = await self.exit_stack.enter_async_context(
            ClientSession(read, write)
        )

        # Initialize the session
        await session.initialize()
        self.sessions[server_name] = session

        # Create and register MCP adapter
        tools = await session.list_tools()
        adapter = MCPToolsAdapter(AdapterConfig({
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema
                }
                for tool in tools.tools
            ]
        }))

        self.adapters[server_name] = adapter
        self.adapter_tools[server_name] = adapter.get_all_tools()

    async def register_adapter(
        self,
        name: str,
        config: Optional[AdapterConfig] = None
    ) -> None:
        """Register a new native CrewAI adapter.

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

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> None:
        """Async context manager exit."""
        await self.exit_stack.aclose()