"""Tools implementation for native CrewAI adapter support with MCP compatibility."""
from typing import Any, Dict, List, Optional, Type, Union
from dataclasses import dataclass
from langchain_core.tools import BaseTool, StructuredTool
from langchain_core.pydantic_v1 import BaseModel, create_model
from mcp.types import Tool as MCPTool
from mcp.types import CallToolResult, TextContent
from crewai_adapters.base import BaseAdapter
from crewai_adapters.types import AdapterConfig, AdapterResponse, AdapterMetadata
from crewai_adapters.exceptions import ConfigurationError
from crewai_adapters.utils import create_metadata
import time

@dataclass
class CrewAITool:
    """Representation of a CrewAI tool."""
    name: str
    description: str
    parameters: Dict[str, Any]
    func: Optional[Any] = None

def _create_schema_model(parameters: Dict[str, Any]) -> Type[BaseModel]:
    """Create a Pydantic model from parameters dict."""
    return create_model(
        'DynamicSchema',
        **{k: (v.get('type', Any), ...) for k, v in parameters.items()}
    )

def _convert_tool_result(result: CallToolResult) -> Union[str, List[str]]:
    """Convert MCP tool result to CrewAI compatible format."""
    text_contents = [content for content in result.content if isinstance(content, TextContent)]
    tool_content = [content.text for content in text_contents]
    return tool_content[0] if len(text_contents) == 1 else tool_content

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
            tool = MCPTool(
                name=tool_config["name"],
                description=tool_config.get("description", ""),
                inputSchema=schema  # Changed from input_schema to inputSchema
            )
            self.tools.append(tool)

    def convert_to_crewai_tool(self, tool: MCPTool) -> BaseTool:
        """Convert MCP tool to CrewAI compatible tool."""
        schema_model = _create_schema_model(tool.inputSchema or {})

        async def tool_executor(**kwargs: Any) -> Any:
            start_time = time.time()
            result = await self.execute(tool_name=tool.name, parameters=kwargs)
            return result.data if result.success else None

        return StructuredTool(
            name=tool.name,
            description=tool.description or "",
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
                error=f"Tool {tool_name} not found"
            )

        try:
            result = await tool.execute(parameters)
            converted_result = _convert_tool_result(result)

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
            tool = CrewAITool(
                name=tool_config["name"],
                description=tool_config.get("description", ""),
                parameters=tool_config.get("parameters", {}),
                func=tool_config.get("func")
            )
            self.tools.append(tool)

    def convert_to_crewai_tool(self, tool: CrewAITool) -> BaseTool:
        """Convert adapter tool to CrewAI tool."""
        schema_model = _create_schema_model(tool.parameters)

        async def tool_executor(**kwargs: Any) -> Any:
            start_time = time.time()
            result = await self.execute(tool_name=tool.name, parameters=kwargs)
            return result.data if result.success else None

        return StructuredTool(
            name=tool.name,
            description=tool.description,
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
                error=f"Tool {tool_name} not found"
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