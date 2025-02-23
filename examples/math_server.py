"""Example math server using native CrewAI adapters."""
import logging
from typing import Dict, Any
from crewai_adapters import BaseAdapter, AdapterConfig, AdapterResponse
from crewai_adapters.tools import CrewAITool
from crewai_adapters.utils import create_metadata
import time

class MathServerAdapter(BaseAdapter):
    """Adapter for math operations."""

    def __init__(self, config: AdapterConfig = None):
        """Initialize the math server adapter."""
        super().__init__(config or AdapterConfig({}))
        self.tools = self._register_tools()

    def _validate_config(self) -> None:
        """No specific validation needed for math operations."""
        pass

    def add(self, a: int, b: int) -> str:
        """Add two numbers."""
        try:
            result = int(a) + int(b)
            return str(result)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid input for addition: {str(e)}")

    def multiply(self, a: int, b: int) -> str:
        """Multiply two numbers."""
        try:
            result = int(a) * int(b)
            return str(result)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid input for multiplication: {str(e)}")

    def _register_tools(self) -> Dict[str, CrewAITool]:
        """Register available math tools."""
        return {
            "add": CrewAITool(
                name="add",
                description="Add two numbers",
                parameters={
                    "type": "object",
                    "properties": {
                        "a": {"type": "integer", "description": "First number"},
                        "b": {"type": "integer", "description": "Second number"}
                    },
                    "required": ["a", "b"]
                },
                func=self.add
            ),
            "multiply": CrewAITool(
                name="multiply",
                description="Multiply two numbers",
                parameters={
                    "type": "object",
                    "properties": {
                        "a": {"type": "integer", "description": "First number"},
                        "b": {"type": "integer", "description": "Second number"}
                    },
                    "required": ["a", "b"]
                },
                func=self.multiply
            )
        }

    async def execute(self, **kwargs: Any) -> AdapterResponse:
        """Execute a math operation."""
        start_time = time.time()
        tool_name = kwargs.get("tool_name")
        parameters = kwargs.get("parameters", {})

        if not tool_name or tool_name not in self.tools:
            return AdapterResponse(
                success=False,
                error=f"Unknown tool: {tool_name}",
                metadata=create_metadata(
                    source=self.__class__.__name__,
                    start_time=start_time
                )
            )

        try:
            tool = self.tools[tool_name]
            result = tool.func(**parameters)

            return AdapterResponse(
                success=True,
                data=result,
                metadata=create_metadata(
                    source=self.__class__.__name__,
                    start_time=start_time
                )
            )
        except Exception as e:
            logging.error(f"Math operation failed: {str(e)}")
            return AdapterResponse(
                success=False,
                error=str(e),
                metadata=create_metadata(
                    source=self.__class__.__name__,
                    start_time=start_time
                )
            )

if __name__ == "__main__":
    import asyncio

    async def main():
        """Run example calculations."""
        adapter = MathServerAdapter()

        # Test addition
        add_result = await adapter.execute(
            tool_name="add",
            parameters={"a": 5, "b": 3}
        )
        print(f"5 + 3 = {add_result.data}")

        # Test multiplication
        mult_result = await adapter.execute(
            tool_name="multiply",
            parameters={"a": 4, "b": 6}
        )
        print(f"4 * 6 = {mult_result.data}")

    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())