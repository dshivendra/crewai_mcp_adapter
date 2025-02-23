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
        # Configure tools
        tool_config = AdapterConfig({
            "tools": [{
                "name": "data_processor",
                "description": "Process data using the adapter",
                "parameters": {
                    "data": {"type": "string", "description": "Data to process"}
                },
                "func": process_data  # Your async function
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
            agent=agent
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

### Custom Tool Implementation

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

# Usage
adapter = CustomToolsAdapter(AdapterConfig({
    "tools": [{
        "name": "custom_processor",
        "description": "Custom data processor",
        "parameters": {
            "data": {"type": "string"}
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

For more examples and implementations, check out the test files in the repository.