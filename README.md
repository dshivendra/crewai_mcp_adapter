# CrewAI Adapters Library

A Python library providing native adapter support for CrewAI, making it easy to extend and integrate with various tools and services.

## Features

- Native CrewAI integration and adapter patterns
- Compatible with existing CrewAI agents and tools
- Consistent API design
- Easy-to-use interface for extending and creating new adapters
- Type-safe implementation
- Comprehensive documentation

## Installation

```bash
pip install crewai-adapters
```

## Quick Start

```python
from crewai_adapters import BaseAdapter, AdapterRegistry
from crewai_adapters.adapters import BasicAdapter

# Create and configure an adapter
adapter = BasicAdapter({"name": "MyAdapter"})

# Execute the adapter
async def main():
    response = await adapter.execute(message="Hello, CrewAI!")
    print(response.data)  # Output: MyAdapter: Hello, CrewAI!

# Register a custom adapter
class CustomAdapter(BaseAdapter):
    def _validate_config(self) -> None:
        pass

    async def execute(self, **kwargs):
        # Your custom implementation here
        pass

AdapterRegistry.register("custom", CustomAdapter)
```

## Documentation

For detailed documentation, visit:
- [Getting Started Guide](docs/index.md)
- [API Reference](docs/api_reference.md)
- [Examples](docs/examples.md)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.