# CrewAI Adapters Documentation

Welcome to the CrewAI Adapters library documentation. This library provides native adapter support for CrewAI, enabling easy integration with various tools and services.

## Overview

CrewAI Adapters is designed to provide a consistent and type-safe way to extend CrewAI functionality through adapters. The library follows modern Python practices and provides comprehensive tooling for creating and managing adapters.

## Key Components

### BaseAdapter
The foundation class for all adapters, providing:
- Standardized initialization and configuration
- Abstract methods for execution and validation
- Type-safe error handling

### AdapterRegistry
Central registry for managing adapters:
- Register new adapter implementations
- Retrieve registered adapters
- List available adapters

### AdapterConfig
Type-safe configuration management:
- JSON Schema validation for tool parameters
- Flexible configuration options
- Runtime validation

### AdapterResponse
Standardized response format:
- Success/failure indication
- Type-safe data handling
- Detailed error information
- Execution metadata

## Getting Started

### Installation

```bash
pip install crewai-adapters
```

### Basic Usage

```python
from crewai import Agent, Task
from crewai_adapters import CrewAIAdapterClient
from crewai_adapters.types import AdapterConfig

async def main():
    async with CrewAIAdapterClient() as client:
        # Register tool
        await client.register_adapter(
            "example",
            AdapterConfig({
                "tools": [{
                    "name": "example_tool",
                    "description": "Example tool",
                    "parameters": {
                        "properties": {
                            "input": {
                                "type": "string",
                                "description": "Input data"
                            }
                        },
                        "required": ["input"]
                    }
                }]
            })
        )

        # Create agent with tools
        agent = Agent(
            name="ExampleAgent",
            goal="Process data",
            tools=client.get_tools()
        )

        # Execute task
        task = Task(
            description="Process input data",
            agent=agent
        )
        result = await task.execute()
```

### Next Steps

- Check out the [Examples](examples.md) for more usage patterns
- Review the [API Reference](api_reference.md) for detailed documentation
- Follow best practices in error handling and configuration

## Features

- Native CrewAI integration and adapter patterns
- Compatible with existing CrewAI agents and tools
- Type-safe implementation with Pydantic
- JSON Schema validation for tool parameters
- Comprehensive error handling
- Detailed execution metadata
- Async/await support
- Extensive documentation and examples

For more detailed information, check out the [API Reference](api_reference.md) and [Examples](examples.md) sections.