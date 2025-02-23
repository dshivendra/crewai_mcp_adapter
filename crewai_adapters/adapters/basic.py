"""Basic adapter implementation for demonstration."""
from typing import Any, Optional
import time
from crewai_adapters.base import BaseAdapter
from crewai_adapters.types import AdapterResponse, AdapterMetadata
from crewai_adapters.utils import create_metadata
from crewai_adapters.exceptions import ConfigurationError

class BasicAdapter(BaseAdapter):
    """A basic adapter implementation for demonstration purposes."""

    def _validate_config(self) -> None:
        """Validate the adapter configuration.

        Raises:
            ConfigurationError: If required fields are missing
        """
        required_fields = ["name"]
        for field in required_fields:
            if field not in self.config:
                raise ConfigurationError(f"Missing required field: {field}")

    async def execute(self, **kwargs: Any) -> AdapterResponse:
        """Execute the basic adapter functionality.

        Args:
            **kwargs: Additional execution parameters

        Returns:
            AdapterResponse with execution results
        """
        start_time = time.time()

        try:
            # Example implementation
            message = kwargs.get("message", "Hello from BasicAdapter!")
            name = self.config["name"]

            result = f"{name}: {message}"

            metadata: AdapterMetadata = create_metadata(
                source=self.__class__.__name__,
                start_time=start_time
            )

            return AdapterResponse(
                success=True,
                data=result,
                metadata=metadata
            )

        except Exception as e:
            error_metadata: AdapterMetadata = create_metadata(
                source=self.__class__.__name__,
                start_time=start_time
            )
            return AdapterResponse(
                success=False,
                error=str(e),
                metadata=error_metadata
            )