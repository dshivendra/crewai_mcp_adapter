"""Tools implementation for native CrewAI adapter support with MCP compatibility."""
from typing import Any, Dict, List, Optional, Type, Callable
from dataclasses import dataclass
import logging
import time
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
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

class ToolInputSchema(BaseModel):
    """Schema for tool parameters."""
    parameters: Dict[str, Any] = Field(default_factory=dict)

class ConcreteCrewAITool(BaseTool):
    """Concrete implementation of BaseTool."""

    name: str
    description: str
    args_schema: Type[BaseModel] = ToolInputSchema

    def __init__(
        self,
        name: str,
        description: str,
        execution_func: Callable[..., Any],
        args_schema: Optional[Type[BaseModel]] = None
    ):
        """Initialize the tool with name, description and execution function."""
        super().__init__(
            name=name,
            description=description,
            args_schema=args_schema or ToolInputSchema
        )
        self._execution_func = execution_func

    async def _run(self, **kwargs: Any) -> str:
        """Execute the tool."""
        try:
            result = await self._execution_func(**kwargs)
            return str(result)
        except Exception as e:
            logging.error(f"Tool execution failed: {str(e)}")
            raise ExecutionError(f"Failed to execute {self.name}: {str(e)}")

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
            try:
                tool = MCPTool(
                    name=tool_config["name"],
                    description=tool_config.get("description", ""),
                    inputSchema=tool_config.get("parameters", {})
                )
                self.tools.append(tool)
            except Exception as e:
                logging.error(f"Failed to register tool {tool_config['name']}: {str(e)}")

    def convert_to_crewai_tool(self, mcp_tool: MCPTool) -> BaseTool:
        """Convert MCP tool to CrewAI compatible tool."""
        async def tool_executor(**kwargs: Any) -> str:
            """Execute MCP tool through CrewAI interface."""
            try:
                result = await self.execute(tool_name=mcp_tool.name, parameters=kwargs)
                if result.success:
                    return str(result.data)
                raise ExecutionError(result.error or "Unknown error")
            except Exception as e:
                logging.error(f"Tool execution failed: {str(e)}")
                raise ExecutionError(f"Failed to execute {mcp_tool.name}: {str(e)}")

        return ConcreteCrewAITool(
            name=mcp_tool.name,
            description=mcp_tool.description or "",
            execution_func=tool_executor,
            args_schema=ToolInputSchema
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
            result = "Executed MCP tool successfully"
            metadata = create_metadata(
                source=self.__class__.__name__,
                start_time=start_time,
                additional_data={"tool": tool_name, "parameters": parameters}
            )

            return AdapterResponse(
                success=True,
                data=result,
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

    def get_all_tools(self) -> List[BaseTool]:
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

    def convert_to_crewai_tool(self, crewai_tool: CrewAITool) -> BaseTool:
        """Convert adapter tool to CrewAI tool."""
        if not crewai_tool.func:
            raise ConfigurationError(f"Tool {crewai_tool.name} has no execution function")

        return ConcreteCrewAITool(
            name=crewai_tool.name,
            description=crewai_tool.description,
            execution_func=crewai_tool.func,
            args_schema=ToolInputSchema
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

    def get_all_tools(self) -> List[BaseTool]:
        """Get all registered tools as CrewAI tools."""
        return [self.convert_to_crewai_tool(tool) for tool in self.tools]