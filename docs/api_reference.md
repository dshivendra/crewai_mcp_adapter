# API Reference

## Base Classes

### BaseAdapter

The foundation class for all CrewAI adapters. Provides core functionality and standardized interface.

```python
class BaseAdapter(ABC):
    def __init__(self, config: Optional[AdapterConfig] = None) -> None:
        """Initialize adapter with configuration."""

    @abstractmethod
    def _validate_config(self) -> None:
        """Validate adapter configuration."""

    @abstractmethod
    async def execute(self, **kwargs: Any) -> AdapterResponse:
        """Execute adapter functionality."""

    @classmethod
    def create(cls: Type[T], **kwargs: Any) -> T:
        """Create adapter instance with configuration."""
```

### AdapterRegistry

Central registry for managing and accessing adapters.

```python
class AdapterRegistry:
    @classmethod
    def register(cls, name: str, adapter_cls: Type[BaseAdapter]) -> None:
        """Register a new adapter."""

    @classmethod
    def get(cls, name: str) -> Type[BaseAdapter]:
        """Get registered adapter by name."""

    @classmethod
    def list_adapters(cls) -> Dict[str, Type[BaseAdapter]]:
        """List all registered adapters."""
```

## Types

### AdapterConfig

Configuration type for adapters.

```python
class AdapterConfig(Dict[str, Any]):
    """Configuration dictionary supporting any key-value pairs."""
```

### AdapterResponse

Standardized response type for adapter execution.

```python
@dataclass
class AdapterResponse:
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
```

## Exceptions

### AdapterError

Base exception for adapter-related errors.

```python
class AdapterError(Exception):
    """Base exception for all adapter errors."""

class ConfigurationError(AdapterError):
    """Configuration validation errors."""

class ExecutionError(AdapterError):
    """Execution-time errors."""

class ValidationError(AdapterError):
    """Validation-related errors."""
```

## Built-in Adapters

### BasicAdapter

A simple adapter implementation for demonstration purposes.

```python
class BasicAdapter(BaseAdapter):
    async def execute(self, **kwargs: Any) -> AdapterResponse:
        """Execute basic functionality."""
```

For more examples and implementations, see the [Examples](examples.md) section.