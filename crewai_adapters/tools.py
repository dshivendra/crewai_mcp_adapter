"""Tools implementation for native CrewAI adapter support."""
from typing import Any, Dict, List, Optional, Type
from dataclasses import dataclass
from crewai.tools import BaseTool, StructuredTool
from crewai_adapters.base import BaseAdapter
from crewai_adapters.types import AdapterConfig, AdapterResponse, AdapterMetadata
from crewai_adapters.exceptions import ConfigurationError
from crewai_adapters.utils import create_metadata

@dataclass
class CrewAITool:
    """Representation of a CrewAI tool."""
    name: str
    description: str
    parameters: Dict[str, Any]
    func: Optional[Any] = None

class CrewAIToolsAdapter(BaseAdapter):
    """Adapter for handling CrewAI tools with native support."""

    def __init__(self, config: Optional[AdapterConfig] = None) -> None:
        """Initialize the CrewAI tools adapter.

        Args:
            config: Optional configuration for the adapter
        """
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
        """Convert an adapter tool to a CrewAI tool.

        Args:
            tool: The tool to convert

        Returns:
            A CrewAI-compatible tool
        """
        async def tool_executor(**kwargs: Any) -> Any:
            result = await self.execute(tool_name=tool.name, parameters=kwargs)
            return result.data if result.success else None

        return StructuredTool(
            name=tool.name,
            description=tool.description,
            func=tool_executor,
            parameters=tool.parameters
        )

    async def execute(self, **kwargs: Any) -> AdapterResponse:
        """Execute a tool operation.

        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            **kwargs: Additional parameters

        Returns:
            AdapterResponse with execution results
        """
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
                additional_data={"tool": tool_name, "error": str(e)}
            )
            return AdapterResponse(
                success=False,
                error=str(e),
                metadata=error_metadata
            )

    def get_all_tools(self) -> List[BaseTool]:
        """Get all registered tools as CrewAI tools.

        Returns:
            List of CrewAI-compatible tools
        """
        return [self.convert_to_crewai_tool(tool) for tool in self.tools]