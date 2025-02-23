
"""Tools implementation for CrewAI adapters."""
from typing import Any, Dict, List, Optional
from crewai_adapters.base import BaseAdapter
from crewai_adapters.types import AdapterResponse, AdapterConfig
from crewai_adapters.exceptions import ConfigurationError
from crewai_adapters.utils import create_metadata

class ToolsAdapter(BaseAdapter):
    """Adapter for handling CrewAI tools integration."""
    
    def _validate_config(self) -> None:
        """Validate the tools configuration."""
        if "tools" not in self.config:
            raise ConfigurationError("Missing required tools configuration")
            
        if not isinstance(self.config["tools"], list):
            raise ConfigurationError("Tools configuration must be a list")
            
    async def execute(self, **kwargs: Any) -> AdapterResponse:
        """Execute tool operations.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            **kwargs: Additional execution parameters
            
        Returns:
            AdapterResponse with tool execution results
        """
        start_time = kwargs.pop("start_time", None)
        tool_name = kwargs.get("tool_name")
        parameters = kwargs.get("parameters", {})
        
        try:
            tool_result = self._execute_tool(tool_name, parameters)
            metadata = create_metadata(
                source=self.__class__.__name__,
                start_time=start_time,
                additional_data={"tool": tool_name}
            )
            
            return AdapterResponse(
                success=True,
                data=tool_result,
                metadata=metadata
            )
            
        except Exception as e:
            return AdapterResponse(
                success=False,
                error=str(e)
            )
            
    def _execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific tool with given parameters.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Tool execution parameters
            
        Returns:
            Tool execution results
            
        Raises:
            ConfigurationError: If tool is not found
        """
        available_tools = {tool["name"]: tool for tool in self.config["tools"]}
        
        if tool_name not in available_tools:
            raise ConfigurationError(f"Tool not found: {tool_name}")
            
        tool_config = available_tools[tool_name]
        
        # Basic tool execution logic
        result = {
            "tool_name": tool_name,
            "status": "executed",
            "parameters": parameters,
            "config": tool_config,
            "result": f"Executed {tool_name} with parameters: {parameters}"
        }
        
        return result
