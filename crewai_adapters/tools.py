"""Tools implementation for native CrewAI adapter support."""
from typing import Any, Dict, List, Optional, Type, Callable, Union, Awaitable
from dataclasses import dataclass
import logging
import time
import asyncio
from crewai.tools import BaseTool
from pydantic import BaseModel, Field, create_model

from crewai_adapters.base import BaseAdapter
from crewai_adapters.types import AdapterConfig, AdapterResponse
from crewai_adapters.exceptions import ConfigurationError, ExecutionError
from crewai_adapters.utils import create_metadata

@dataclass
class CrewAITool:
    """Representation of a CrewAI tool."""
    name: str
    description: str
    parameters: Union[Dict[str, Any], str]
    func: Optional[Callable[..., Union[str, Awaitable[str]]]] = None

class ToolInputSchema(BaseModel):
    """Schema for tool parameters."""
    test: str = Field(..., description="Test parameter")

class ConcreteCrewAITool(BaseTool):
    """Concrete implementation of CrewAI tool."""
    name: str = "default_tool"
    description: str = "Default tool description"
    args_schema: Type[BaseModel] = ToolInputSchema

    def __init__(
        self,
        name: str,
        description: str,
        execution_func: Callable[..., Union[str, Awaitable[str]]],
        tool_args_schema: Optional[Type[BaseModel]] = None
    ):
        """Initialize the tool."""
        super().__init__()
        self.name = name
        self.description = description
        if tool_args_schema:
            self.args_schema = tool_args_schema
        self._execution_func = execution_func

    def _run(self, **kwargs: Any) -> str:
        """Execute the tool synchronously."""
        try:
            result = self._execution_func(**kwargs)
            if asyncio.iscoroutine(result):
                result = asyncio.get_event_loop().run_until_complete(result)
            return str(result)
        except Exception as e:
            logging.error(f"Tool execution failed: {str(e)}")
            raise ExecutionError(f"Failed to execute {self.name}: {str(e)}")

    async def _arun(self, **kwargs: Any) -> str:
        """Execute the tool asynchronously."""
        try:
            result = self._execution_func(**kwargs)
            if asyncio.iscoroutine(result):
                result = await result
            return str(result)
        except Exception as e:
            logging.error(f"Tool execution failed: {str(e)}")
            raise ExecutionError(f"Failed to execute {self.name}: {str(e)}")

def _create_tool_schema(params: Dict[str, Any], schema_name: str) -> Type[BaseModel]:
    """Create a Pydantic model for tool parameters."""
    fields = {}

    # Handle JSON Schema format
    if "properties" in params:
        properties = params["properties"]
        for field_name, field_props in properties.items():
            field_type = field_props.get("type", "string")
            field_desc = field_props.get("description", "")
            python_type = str if field_type == "string" else Any
            fields[field_name] = (python_type, Field(..., description=field_desc))
    else:
        # Handle direct parameter definitions
        for field_name, field_info in params.items():
            if isinstance(field_info, dict):
                field_desc = field_info.get("description", "")
                fields[field_name] = (str, Field(..., description=field_desc))
            else:
                fields[field_name] = (str, Field(...))

    return create_model(schema_name, **fields)

class CrewAIToolsAdapter(BaseAdapter):
    """Adapter for handling native CrewAI tools."""

    def __init__(self, config: Optional[AdapterConfig] = None) -> None:
        """Initialize adapter with config."""
        super().__init__(config)
        self.tools: List[CrewAITool] = []
        self._register_tools()

    def _validate_config(self) -> None:
        """Validate adapter configuration."""
        if not self.config.get("tools"):
            raise ConfigurationError("Tools configuration is required")

    def _register_tools(self) -> None:
        """Register native CrewAI tools from configuration."""
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

    def _get_default_func(self, tool_name: str) -> Callable[..., str]:
        """Get default execution function for a tool."""
        def default_func(**kwargs: Any) -> str:
            return f"Executed {tool_name} with parameters {kwargs}"
        return default_func

    def convert_to_crewai_tool(self, crewai_tool: CrewAITool) -> BaseTool:
        """Convert adapter tool to CrewAI tool."""
        execution_func = crewai_tool.func or self._get_default_func(crewai_tool.name)

        # Parse parameters and create schema
        params = crewai_tool.parameters
        if isinstance(params, str):
            # If parameters is a string, use default schema
            tool_schema = ToolInputSchema
        else:
            # Create dynamic schema
            schema_name = f"{crewai_tool.name.title()}Schema"
            tool_schema = _create_tool_schema(params, schema_name)

        return ConcreteCrewAITool(
            name=crewai_tool.name,
            description=crewai_tool.description,
            execution_func=execution_func,
            tool_args_schema=tool_schema
        )

    def get_all_tools(self) -> List[BaseTool]:
        """Get all registered tools as CrewAI tools."""
        return [self.convert_to_crewai_tool(tool) for tool in self.tools]

    async def execute(self, **kwargs: Any) -> AdapterResponse:
        """Execute tool operation."""
        start_time = time.time()
        tool_name = kwargs.get("tool_name")
        parameters = kwargs.get("parameters", {})

        if not tool_name:
            return AdapterResponse(
                success=False,
                error="Tool name is required",
                metadata=create_metadata(
                    source=self.__class__.__name__,
                    start_time=start_time
                )
            )

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

            execution_func = tool.func or self._get_default_func(tool_name)
            result = execution_func(**parameters)
            if asyncio.iscoroutine(result):
                result = await result

            return AdapterResponse(
                success=True,
                data=str(result),
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

class MCPToolsAdapter(CrewAIToolsAdapter):
    """Adapter for handling MCP protocol tools."""

    def __init__(self, config: Optional[AdapterConfig] = None) -> None:
        """Initialize adapter with config."""
        super().__init__(config)

    def _register_tools(self) -> None:
        """Register MCP tools from configuration."""
        for tool_config in self.config.get("tools", []):
            try:
                tool = CrewAITool(
                    name=tool_config["name"],
                    description=tool_config.get("description", ""),
                    parameters=tool_config.get("parameters", {}),
                    func=None  # MCP tools use default execution
                )
                self.tools.append(tool)
            except Exception as e:
                logging.error(f"Failed to register tool {tool_config.get('name')}: {str(e)}")