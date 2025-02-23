"""Tools implementation following LangChain MCP adapter pattern."""
from typing import Any, Dict, List, Optional
from mcp import MCPTool, MCPToolkit
from crewai_adapters.base import BaseAdapter
from crewai_adapters.types import AdapterResponse
from crewai_adapters.exceptions import ConfigurationError

class MCPToolsAdapter(BaseAdapter):
    """Adapter for handling CrewAI tools using MCP protocol."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self.toolkit = MCPToolkit()
        self._register_tools()

    def _validate_config(self) -> None:
        if not self.config.get("tools"):
            raise ConfigurationError("Tools configuration is required")

    def _register_tools(self) -> None:
        """Register tools from config with MCP toolkit."""
        for tool_config in self.config.get("tools", []):
            tool = MCPTool(
                name=tool_config["name"],
                description=tool_config.get("description", ""),
                parameters=tool_config.get("parameters", {})
            )
            self.toolkit.add_tool(tool)

    async def execute(self, **kwargs: Any) -> AdapterResponse:
        """Execute tool operation using MCP protocol.

        Args:
            tool_name: Name of tool to execute
            parameters: Tool parameters
            **kwargs: Additional parameters

        Returns:
            AdapterResponse with execution results
        """
        tool_name = kwargs.get("tool_name")
        parameters = kwargs.get("parameters", {})

        if not tool_name:
            raise ConfigurationError("Tool name is required")

        try:
            tool = self.toolkit.get_tool(tool_name)
            result = await tool.execute(parameters)

            return AdapterResponse(
                success=True,
                data=result,
                metadata={
                    "tool": tool_name,
                    "parameters": parameters
                }
            )

        except Exception as e:
            return AdapterResponse(
                success=False,
                error=str(e)
            )