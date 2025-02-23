"""Example math server using CrewAI adapters."""
from typing import Dict, Any
from crewai_adapters import BaseAdapter, AdapterConfig, AdapterResponse
from crewai_adapters.tools import CrewAITool
from crewai_adapters.utils import create_metadata
import time

class MathServerAdapter(BaseAdapter):
    """Adapter for math operations."""

    def __init__(self, config: AdapterConfig = None):
        super().__init__(config or AdapterConfig({}))
        self.tools = self._register_tools()

    def _validate_config(self) -> None:
        """No specific validation needed for math operations."""
        pass

    async def add(self, a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    async def multiply(self, a: int, b: int) -> int:
        """Multiply two numbers."""
        return a * b

    def _register_tools(self) -> Dict[str, CrewAITool]:
        """Register available math tools."""
        return {
            "add": CrewAITool(
                name="add",
                description="Add two numbers",
                parameters={
                    "a": {"type": "integer", "description": "First number"},
                    "b": {"type": "integer", "description": "Second number"}
                },
                func=self.add
            ),
            "multiply": CrewAITool(
                name="multiply",
                description="Multiply two numbers",
                parameters={
                    "a": {"type": "integer", "description": "First number"},
                    "b": {"type": "integer", "description": "Second number"}
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
            result = await tool.func(**parameters)

            return AdapterResponse(
                success=True,
                data=result,
                metadata=create_metadata(
                    source=self.__class__.__name__,
                    start_time=start_time
                )
            )
        except Exception as e:
            return AdapterResponse(
                success=False,
                error=str(e),
                metadata=create_metadata(
                    source=self.__class__.__name__,
                    start_time=start_time
                )
            )

if __name__ == "__main__":
    # Example usage
    import asyncio

    async def main():
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

    asyncio.run(main())