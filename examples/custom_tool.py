"""Example of creating custom CrewAI tools using adapters."""
from typing import Type, Dict, Any, Callable
from crewai.tools import BaseTool, tool
from pydantic import BaseModel, Field, create_model
from crewai_adapters import CrewAIToolsAdapter, AdapterConfig
from crewai_adapters.types import AdapterResponse
from crewai_adapters.exceptions import ExecutionError
import logging

class SearchInput(BaseModel):
    """Input schema for search tool."""
    query: str = Field(..., description="Search query to execute")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum number of results to return")

class CustomSearchTool(BaseTool):
    """Example custom search tool."""
    name: str = "web_search"
    description: str = "Search the web for information"
    args_schema: Type[BaseModel] = SearchInput

    def _run(self, query: str, limit: int = 10) -> str:
        """Execute the search synchronously."""
        if not query.strip():
            raise ExecutionError("Search query cannot be empty")

        if limit < 1 or limit > 100:
            raise ExecutionError("Limit must be between 1 and 100")

        return f"Found {limit} results for: {query}"

    async def _arun(self, query: str, limit: int = 10) -> str:
        """Execute the search asynchronously."""
        return self._run(query=query, limit=limit)

def create_cached_tool() -> BaseTool:
    """Create a tool with caching."""
    @tool("cached_search")
    def cached_search_tool(query: str) -> str:
        """Search with caching capability."""
        if not query.strip():
            raise ExecutionError("Search query cannot be empty")
        return f"Cached search result for: {query}"

    def cache_strategy(kwargs: Dict[str, Any], result: str) -> bool:
        """Custom caching strategy."""
        # Cache results for queries longer than 5 characters
        return len(kwargs.get("query", "")) > 5

    cached_search_tool.cache_function = cache_strategy
    return cached_search_tool

async def run_example():
    """Run example with both tool types."""
    try:
        logging.info("Setting up custom tools example...")
        # Create adapter with custom tool configuration
        adapter = CrewAIToolsAdapter(AdapterConfig({
            "tools": [{
                "name": "web_search",
                "description": "Search the web for information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query to execute"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 100
                        }
                    },
                    "required": ["query"]
                }
            }]
        }))

        logging.info("Testing class-based tool...")
        # Test successful execution
        response = await adapter.execute(
            tool_name="web_search",
            parameters={"query": "python programming", "limit": 5}
        )
        print(f"Class-based tool result: {response.data}")

        logging.info("Testing error handling...")
        # Test empty query error
        try:
            await adapter.execute(
                tool_name="web_search",
                parameters={"query": "", "limit": 5}
            )
        except ExecutionError as e:
            print(f"Expected error caught: {e}")

        logging.info("Testing cached tool...")
        # Test cached tool execution
        cached_tool = create_cached_tool()
        result = cached_tool.run(query="python caching example")
        print(f"Cached tool result: {result}")

        # Verify caching behavior
        would_cache = cached_tool.cache_function({"query": "python caching"}, result)
        print(f"Would cache result: {would_cache}")

        # Test cached tool error handling
        try:
            cached_tool.run(query="")
        except ExecutionError as e:
            print(f"Expected cached tool error caught: {e}")

    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}")
        print(f"Unexpected error occurred: {e}")
        raise

if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_example())