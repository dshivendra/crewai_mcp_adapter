# Usage Examples

## Basic CrewAI Adapter Usage

### Tool Integration Example

```python
from crewai import Agent, Task
from crewai_adapters import CrewAIAdapterClient, CrewAITool
from crewai_adapters.types import AdapterConfig

async def setup_tools():
    # Create and configure the adapter client
    async with CrewAIAdapterClient() as client:
        # Configure tools with proper schema
        tool_config = AdapterConfig({
            "tools": [{
                "name": "data_processor",
                "description": "Process data using the adapter",
                "parameters": {
                    "properties": {
                        "data": {
                            "type": "string",
                            "description": "Data to process"
                        }
                    },
                    "type": "object",
                    "required": ["data"]
                }
            }]
        })

        # Register the adapter
        await client.register_adapter("data_tools", tool_config)

        # Get all tools
        tools = client.get_tools()

        # Create an agent with the tools
        agent = Agent(
            name="DataAgent",
            goal="Process data efficiently",
            backstory="I am an agent that processes data",
            tools=tools
        )

        # Create and execute a task
        task = Task(
            description="Process the given dataset",
            agent=agent,
            expected_output="Processed data results"  # Added expected output
        )

        return task

# Example async tool function
async def process_data(data: str) -> str:
    return f"Processed: {data}"

# Usage in CrewAI
task = await setup_tools()
result = await task.execute()
```

## Advanced Usage

This section demonstrates two common patterns for implementing custom tools: class-based and decorator-based approaches.  Both approaches leverage CrewAI's tool framework for seamless integration.


### Class-Based Tool Implementation

```python
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class SearchInput(BaseModel):
    """Input schema for search tool."""
    query: str = Field(..., description="Search query to execute")
    limit: int = Field(default=10, description="Maximum number of results")

class CustomSearchTool(BaseTool):
    """Example custom search tool."""
    name: str = "web_search"
    description: str = "Search the web for information"
    args_schema: Type[BaseModel] = SearchInput

    def _run(self, query: str, limit: int = 10) -> str:
        """Execute search synchronously."""
        return f"Found {limit} results for: {query}"

    async def _arun(self, query: str, limit: int = 10) -> str:
        """Execute search asynchronously."""
        return self._run(query=query, limit=limit)
```

### Decorator-Based Tool with Caching

```python
from crewai.tools import tool

@tool("cached_search")
def cached_search_tool(query: str) -> str:
    """Search with caching capability."""
    return f"Cached search result for: {query}"

def cache_strategy(kwargs: dict, result: str) -> bool:
    """Custom caching strategy."""
    return len(kwargs.get("query", "")) > 5

cached_search_tool.cache_function = cache_strategy

# Usage
result = cached_search_tool.run(query="example search")
```

### Custom Adapter Implementation

```python
from crewai_adapters import CrewAIToolsAdapter, CrewAITool
from crewai_adapters.types import AdapterConfig

class CustomToolsAdapter(CrewAIToolsAdapter):
    async def execute(self, **kwargs):
        tool_name = kwargs.get("tool_name")
        parameters = kwargs.get("parameters", {})

        if tool_name == "custom_processor":
            # Custom implementation
            result = await self.process_custom_data(parameters)
            return AdapterResponse(
                success=True,
                data=result
            )

        return await super().execute(**kwargs)

    async def process_custom_data(self, parameters):
        # Your custom processing logic
        return f"Custom processed: {parameters.get('data')}"

# Usage with proper schema validation
adapter = CustomToolsAdapter(AdapterConfig({
    "tools": [{
        "name": "custom_processor",
        "description": "Custom data processor",
        "parameters": {
            "properties": {
                "data": {
                    "type": "string",
                    "description": "Data to process"
                }
            },
            "type": "object",
            "required": ["data"]
        }
    }]
}))

# Get CrewAI compatible tools
crewai_tools = adapter.get_all_tools()
```

## Error Handling

### Proper Error Management

```python
from crewai_adapters.exceptions import AdapterError, ConfigurationError

async def safe_execute_adapter(adapter, **kwargs):
    try:
        response = await adapter.execute(**kwargs)
        if not response.success:
            print(f"Execution failed: {response.error}")
            return None
        return response.data
    except ConfigurationError as e:
        print(f"Configuration error: {str(e)}")
        return None
    except AdapterError as e:
        print(f"Adapter error: {str(e)}")
        return None
```

## Parameter Schema Examples

### JSON Schema Format

```python
# Using JSON Schema format for parameters
tool_config = {
    "name": "advanced_processor",
    "description": "Process data with multiple parameters",
    "parameters": {
        "type": "object",
        "properties": {
            "input_data": {
                "type": "string",
                "description": "Input data to process"
            },
            "processing_level": {
                "type": "string",
                "description": "Level of processing",
                "enum": ["basic", "advanced", "expert"]
            }
        },
        "required": ["input_data", "processing_level"]
    }
}

# Usage
adapter = CrewAIToolsAdapter(AdapterConfig({
    "tools": [tool_config]
}))
```

For more examples and implementations, check out the test files in the repository.