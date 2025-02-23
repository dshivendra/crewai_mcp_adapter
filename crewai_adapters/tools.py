"""Tools implementation for native CrewAI adapter support."""
from typing import Any, Dict, List, Optional, Type, Callable
from dataclasses import dataclass
import logging
import time
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from crewai_adapters.base import BaseAdapter
from crewai_adapters.types import AdapterConfig, AdapterResponse
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
    test: str = Field(description="Test parameter")

class ConcreteCrewAITool(BaseTool):
    """Concrete implementation of CrewAI tool."""

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
        validate_assignment = False

    def __init__(
        self,
        name: str,
        description: str,
        execution_func: Callable[..., Any],
        tool_args_schema: Optional[Type[BaseModel]] = None
    ):
        """Initialize the tool."""
        self._name = name
        self._description = description
        self._tool_args_schema = tool_args_schema or ToolInputSchema
        self._execution_func = execution_func
        super().__init__()

    @property
    def name(self) -> str:
        """Get tool name."""
        return self._name

    @property
    def description(self) -> str:
        """Get tool description."""
        return self._description

    @property
    def args_schema(self) -> Type[BaseModel]:
        """Get argument schema."""
        return self._tool_args_schema

    async def _run(self, **kwargs: Any) -> str:
        """Execute the tool."""
        try:
            result = await self._execution_func(**kwargs)
            return str(result)
        except Exception as e:
            logging.error(f"Tool execution failed: {str(e)}")
            raise ExecutionError(f"Failed to execute {self.name}: {str(e)}")

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

    def _get_default_func(self, tool_name: str) -> Callable[..., Any]:
        """Get default execution function for a tool."""
        async def default_func(**kwargs: Any) -> str:
            return f"Executed {tool_name} with parameters {kwargs}"
        return default_func

    def convert_to_crewai_tool(self, crewai_tool: CrewAITool) -> BaseTool:
        """Convert adapter tool to CrewAI tool."""
        execution_func = crewai_tool.func or self._get_default_func(crewai_tool.name)

        return ConcreteCrewAITool(
            name=crewai_tool.name,
            description=crewai_tool.description,
            execution_func=execution_func,
            tool_args_schema=ToolInputSchema
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
            result = await execution_func(**parameters)

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