
"""Context protocol client implementation for CrewAI adapters."""
from typing import Any, Dict, List, Optional
from crewai_adapters.base import BaseAdapter
from crewai_adapters.types import AdapterResponse, AdapterConfig
from crewai_adapters.exceptions import ConfigurationError
from crewai_adapters.utils import create_metadata

class ContextProtocolClient(BaseAdapter):
    """Client for handling model context protocol interactions."""
    
    def _validate_config(self) -> None:
        """Validate the context protocol configuration."""
        required_fields = ["model_name", "context_size"]
        for field in required_fields:
            if field not in self.config:
                raise ConfigurationError(f"Missing required field: {field}")
                
        if not isinstance(self.config["context_size"], int):
            raise ConfigurationError("context_size must be an integer")
            
    async def execute(self, **kwargs: Any) -> AdapterResponse:
        """Execute context protocol operations.
        
        Args:
            context: Optional context to include
            messages: List of messages to process
            **kwargs: Additional execution parameters
            
        Returns:
            AdapterResponse with processed context
        """
        start_time = kwargs.pop("start_time", None)
        context = kwargs.get("context", "")
        messages = kwargs.get("messages", [])
        
        try:
            processed_context = self._process_context(context, messages)
            metadata = create_metadata(
                source=self.__class__.__name__,
                start_time=start_time,
                additional_data={"model": self.config["model_name"]}
            )
            
            return AdapterResponse(
                success=True,
                data=processed_context,
                metadata=metadata
            )
            
        except Exception as e:
            return AdapterResponse(
                success=False,
                error=str(e)
            )
            
    def _process_context(self, context: str, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process context and messages according to model requirements.
        
        Args:
            context: Base context string
            messages: List of message dictionaries
            
        Returns:
            Processed context data
        """
        context_size = self.config["context_size"]
        model_name = self.config["model_name"]
        
        # Basic context processing logic
        processed_data = {
            "model": model_name,
            "context": context[:context_size],
            "messages": messages[:context_size],
            "metadata": {
                "original_context_length": len(context),
                "truncated": len(context) > context_size
            }
        }
        
        return processed_data
