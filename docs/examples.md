# Usage Examples

## Basic Adapter Usage

### Simple Message Processing

```python
from crewai_adapters.adapters import BasicAdapter

async def process_message():
    adapter = BasicAdapter({"name": "MessageProcessor"})
    response = await adapter.execute(message="Process this message")

    if response.success:
        print(f"Processed: {response.data}")
        print(f"Processing time: {response.metadata['duration']}s")
    else:
        print(f"Error: {response.error}")
```

## Custom Adapter Implementation

### Creating a Custom API Adapter

```python
from crewai_adapters import BaseAdapter, AdapterResponse
from crewai_adapters.utils import create_metadata
import aiohttp
import time

class APIAdapter(BaseAdapter):
    def _validate_config(self) -> None:
        required = ["api_key", "base_url"]
        for field in required:
            if field not in self.config:
                raise ConfigurationError(f"Missing {field}")

    async def execute(self, **kwargs) -> AdapterResponse:
        start_time = time.time()

        try:
            endpoint = kwargs.get("endpoint", "")
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.config['base_url']}/{endpoint}",
                    headers={"Authorization": f"Bearer {self.config['api_key']}"}
                ) as response:
                    data = await response.json()

                    return AdapterResponse(
                        success=True,
                        data=data,
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

# Register the adapter
AdapterRegistry.register("api", APIAdapter)

# Usage
adapter = APIAdapter({
    "api_key": "your-api-key",
    "base_url": "https://api.example.com"
})
response = await adapter.execute(endpoint="users")
```

## Working with CrewAI

### Integration Example

```python
from crewai import Agent, Task, Crew
from crewai_adapters.adapters import BasicAdapter

# Create an adapter
data_processor = BasicAdapter({"name": "DataProcessor"})

# Create an agent that uses the adapter
agent = Agent(
    name="ProcessingAgent",
    goal="Process data using adapters",
    backstory="I am an agent that processes data using various adapters",
    tools=[data_processor.execute]
)

# Create a task
task = Task(
    description="Process some data",
    agent=agent
)

# Create and run the crew
crew = Crew(
    agents=[agent],
    tasks=[task]
)

result = crew.kickoff()
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

For more examples and use cases, check out the [test files](../tests/) in the repository.