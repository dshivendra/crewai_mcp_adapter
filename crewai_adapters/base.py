"""Base adapter implementation and registry."""
from typing import Any, Dict, Optional, Type, TypeVar
from abc import ABC, abstractmethod
from crewai_adapters.types import AdapterConfig, AdapterResponse
from crewai_adapters.exceptions import AdapterError

T = TypeVar("T", bound="BaseAdapter")

class BaseAdapter(ABC):
    """Base class for all CrewAI adapters."""
    
    def __init__(self, config: Optional[AdapterConfig] = None) -> None:
        """Initialize the adapter with optional configuration.
        
        Args:
            config: Configuration dictionary for the adapter
        """
        self.config = config or {}
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self) -> None:
        """Validate the adapter configuration."""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs: Any) -> AdapterResponse:
        """Execute the adapter's main functionality.
        
        Args:
            **kwargs: Keyword arguments for the execution
            
        Returns:
            AdapterResponse: The response from the adapter execution
            
        Raises:
            AdapterError: If execution fails
        """
        pass
    
    @classmethod
    def create(cls: Type[T], **kwargs: Any) -> T:
        """Create a new instance of the adapter.
        
        Args:
            **kwargs: Configuration parameters for the adapter
            
        Returns:
            A new instance of the adapter
        """
        config = AdapterConfig(kwargs)
        return cls(config=config)

class AdapterRegistry:
    """Registry for managing adapters."""
    
    _adapters: Dict[str, Type[BaseAdapter]] = {}
    
    @classmethod
    def register(cls, name: str, adapter_cls: Type[BaseAdapter]) -> None:
        """Register a new adapter.
        
        Args:
            name: Name of the adapter
            adapter_cls: Adapter class to register
        """
        if name in cls._adapters:
            raise AdapterError(f"Adapter '{name}' already registered")
        cls._adapters[name] = adapter_cls
    
    @classmethod
    def get(cls, name: str) -> Type[BaseAdapter]:
        """Get a registered adapter by name.
        
        Args:
            name: Name of the adapter to retrieve
            
        Returns:
            The adapter class
            
        Raises:
            AdapterError: If adapter is not found
        """
        if name not in cls._adapters:
            raise AdapterError(f"Adapter '{name}' not found")
        return cls._adapters[name]
    
    @classmethod
    def list_adapters(cls) -> Dict[str, Type[BaseAdapter]]:
        """List all registered adapters.
        
        Returns:
            Dictionary of registered adapters
        """
        return cls._adapters.copy()
