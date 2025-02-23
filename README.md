# CrewAI MCP Adapter

A Python library extending CrewAI's adapter ecosystem with [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) integration support and comprehensive tooling for custom agent and tool development.

## Features

- 🔌 Native CrewAI integration and adapter patterns
- 🛠️ MCP protocol support for tool integration
- 🧩 Easy-to-use interface for extending and creating new adapters
- 📝 Type-safe implementation with Pydantic
- 🔍 JSON Schema validation for tool parameters
- 🚀 Async/await support
- 📊 Detailed execution metadata

## Installation

```bash
pip install crewai-adapters
```

## Quick Start

```python
from crewai import Agent, Task
from crewai_adapters import CrewAIAdapterClient
from crewai_adapters.types import AdapterConfig

async def main():
    async with CrewAIAdapterClient() as client:
        # Connect to MCP server
        await client.connect_to_mcp_server(
            "math",
            command="python",
            args=["math_server.py"]
        )

        # Create agent with tools
        agent = Agent(
            name="Calculator",
            goal="Perform calculations",
            tools=client.get_tools()
        )

        # Execute task
        task = Task(
            description="Calculate (3 + 5) × 12",
            agent=agent
        )
        result = await task.execute()
        print(f"Result: {result}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Documentation

For detailed documentation, see:
- [Getting Started Guide](docs/index.md)
- [API Reference](docs/api_reference.md)
- [Examples](docs/examples.md)

## Development

### Prerequisites

- Python 3.11 or higher
- `crewai` package
- `pydantic` package
- `mcp` package

### Install Development Dependencies

```bash
pip install -e ".[test,docs]"
```

### Running Tests

```bash
pytest tests/ -v
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.