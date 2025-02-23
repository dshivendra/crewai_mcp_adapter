"""Utility functions for CrewAI adapters."""
import time
from typing import Any, Dict, Optional
from datetime import datetime
from crewai_adapters.types import AdapterMetadata

def create_metadata(
    source: str,
    start_time: float,
    additional_data: Optional[Dict[str, Any]] = None
) -> AdapterMetadata:
    """Create metadata for adapter responses.

    Args:
        source: Source of the adapter execution
        start_time: Start time for duration calculation
        additional_data: Additional metadata to include

    Returns:
        AdapterMetadata object
    """
    duration = time.time() - start_time

    metadata: AdapterMetadata = {
        "timestamp": datetime.utcnow().isoformat(),
        "duration": duration,
        "source": source,
        "additional_data": additional_data
    }

    return metadata

def validate_string_field(field: Any, field_name: str) -> None:
    """Validate that a field is a non-empty string.

    Args:
        field: Field to validate
        field_name: Name of the field for error messages

    Raises:
        ValueError: If validation fails
    """
    if not isinstance(field, str) or not field.strip():
        raise ValueError(f"{field_name} must be a non-empty string")