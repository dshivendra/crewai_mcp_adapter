"""Tools implementation for native CrewAI adapter support with MCP compatibility."""
from typing import Any, Dict, List, Optional, Type, Union
from dataclasses import dataclass
import logging
import time
from crewai.tools import Tool
from pydantic import BaseModel, create_model, Field
from mcp.types import Tool as MCPTool, CallToolResult, TextContent

from crewai_adapters.base import BaseAdapter
from crewai_adapters.types import AdapterConfig, AdapterResponse, AdapterMetadata
from crewai_adapters.exceptions import ConfigurationError, ExecutionError
from crewai_adapters.utils import create_metadata

@dataclass
class CrewAITool:
    """Representation of a CrewAI tool."""
    name: str
    description: str
    parameters: Dict[str, Any]
    func: Optional[Any] = None

def _create_schema_model(parameters: Dict[str, Any]) -> Type[BaseModel]:
    """Create a Pydantic model from parameters dict."""
    fields = {
        name: (field.get('type', Any), Field(..., description=field.get('description', '')))
        for name, field in parameters.items()
    }
    return create_model('DynamicSchema', **fields)

class MCPToolsAdapter(BaseAdapter):
    """Adapter for handling CrewAI tools using MCP protocol."""

    def __init__(self, config: Optional[AdapterConfig] = None) -> None:
        super().__init__(config)
        self.tools: List[MCPTool] = []
        self._register_tools()

    def _validate_config(self) -> None:
        if not self.config.get("tools"):
            raise ConfigurationError("Tools configuration is required")

    def _register_tools(self) -> None:
        """Register MCP tools from configuration."""
        for tool_config in self.config.get("tools", []):
            schema = tool_config.get("parameters", {})
            try:
                tool = MCPTool(
                    name=tool_config["name"],
                    description=tool_config.get("description", ""),
                    inputSchema=schema
                )
                self.tools.append(tool)
            except Exception as e:
                logging.error(f"Failed to register tool {tool_config['name']}: {str(e)}")

    def convert_to_crewai_tool(self, mcp_tool: MCPTool) -> Tool:
        """Convert MCP tool to CrewAI compatible tool."""
        schema_model = _create_schema_model(mcp_tool.inputSchema or {})

        async def tool_executor(**kwargs: Any) -> Any:
            start_time = time.time()
            try:
                result = await self.execute(tool_name=mcp_tool.name, parameters=kwargs)
                return result.data if result.success else None
            except Exception as e:
                logging.error(f"Tool execution failed: {str(e)}")
                raise ExecutionError(f"Failed to execute {mcp_tool.name}: {str(e)}")

        return Tool(
            name=mcp_tool.name,
            description=mcp_tool.description or "",
            func=tool_executor,
            args_schema=schema_model
        )

    async def execute(self, **kwargs: Any) -> AdapterResponse:
        """Execute MCP tool operation."""
        start_time = time.time()
        tool_name = kwargs.get("tool_name")
        parameters = kwargs.get("parameters", {})

        if not tool_name:
            raise ConfigurationError("Tool name is required")

        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            return AdapterResponse(
                success=False,
                error=f"Tool {tool_name} not found",
                metadata=create_metadata(
                    source=self.__class__.__name__,
                    start_time=start_time
                )
            )

        try:
            result = await tool.execute(parameters)
            text_contents = [content for content in result.content if isinstance(content, TextContent)]
            converted_result = "\n".join(content.text for content in text_contents)

            metadata = create_metadata(
                source=self.__class__.__name__,
                start_time=start_time,
                additional_data={"tool": tool_name, "parameters": parameters}
            )

            return AdapterResponse(
                success=True,
                data=converted_result,
                metadata=metadata
            )

        except Exception as e:
            error_metadata = create_metadata(
                source=self.__class__.__name__,
                start_time=start_time,
                additional_data={"tool": tool_name, "error": str(e)}
            )
            return AdapterResponse(
                success=False,
                error=str(e),
                metadata=error_metadata
            )

    def get_all_tools(self) -> List[Tool]:
        """Get all registered tools as CrewAI tools."""
        return [self.convert_to_crewai_tool(tool) for tool in self.tools]

class CrewAIToolsAdapter(BaseAdapter):
    """Adapter for handling native CrewAI tools."""

    def __init__(self, config: Optional[AdapterConfig] = None) -> None:
        super().__init__(config)
        self.tools: List[CrewAITool] = []
        self._register_tools()

    def _validate_config(self) -> None:
        """Validate adapter configuration."""
        if not self.config.get("tools"):
            raise ConfigurationError("Tools configuration is required")

    def _register_tools(self) -> None:
        """Register tools from configuration."""
        for tool_config in self.config.get("tools", []):
            try:
                tool = CrewAITool(
                    name=tool_config["name"],
                    description=tool_config.get("description", ""),
                    parameters=tool_config.get("parameters", {}),
                    func=tool_config.get("func")
                )
                self.tools.append(tool)
            except Exception as e:
                logging.error(f"Failed to register tool {tool_config.get('name')}: {str(e)}")

    def convert_to_crewai_tool(self, crewai_tool: CrewAITool) -> Tool:
        """Convert adapter tool to CrewAI tool."""
        schema_model = _create_schema_model(crewai_tool.parameters)

        async def tool_executor(**kwargs: Any) -> Any:
            start_time = time.time()
            try:
                result = await self.execute(tool_name=crewai_tool.name, parameters=kwargs)
                return result.data if result.success else None
            except Exception as e:
                logging.error(f"Tool execution failed: {str(e)}")
                raise ExecutionError(f"Failed to execute {crewai_tool.name}: {str(e)}")

        return Tool(
            name=crewai_tool.name,
            description=crewai_tool.description,
            func=tool_executor,
            args_schema=schema_model
        )

    async def execute(self, **kwargs: Any) -> AdapterResponse:
        """Execute native CrewAI tool operation."""
        start_time = time.time()
        tool_name = kwargs.get("tool_name")
        parameters = kwargs.get("parameters", {})

        if not tool_name:
            raise ConfigurationError("Tool name is required")

        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            return AdapterResponse(
                success=False,
                error=f"Tool {tool_name} not found",
                metadata=create_metadata(
                    source=self.__class__.__name__,
                    start_time=start_time
                )
            )

        try:
            metadata = create_metadata(
                source=self.__class__.__name__,
                start_time=start_time,
                additional_data={"tool": tool_name, "parameters": parameters}
            )

            if tool.func:
                result = await tool.func(**parameters)
                return AdapterResponse(
                    success=True,
                    data=result,
                    metadata=metadata
                )

            return AdapterResponse(
                success=False,
                error="Tool function not implemented",
                metadata=metadata
            )

        except Exception as e:
            error_metadata = create_metadata(
                source=self.__class__.__name__,
                start_time=start_time,
                additional_data={"tool": tool_name, "error": str(e)}
            )
            return AdapterResponse(
                success=False,
                error=str(e),
                metadata=error_metadata
            )

    def get_all_tools(self) -> List[Tool]:
        """Get all registered tools as CrewAI tools."""
        return [self.convert_to_crewai_tool(tool) for tool in self.tools]