"""Type definitions for CrewAI adapters."""
from typing import Any, Dict, Optional, TypedDict, Union
from dataclasses import dataclass

class AdapterConfig(Dict[str, Any]):
    """Configuration type for adapters."""
    pass

class AdapterMetadata(TypedDict, total=False):
    """Metadata for adapter responses."""

    timestamp: str
    duration: float
    source: str
    # Allow additional fields
    additional_data: Dict[str, Any]

@dataclass
class AdapterResponse:
    """Response type for adapter execution."""

    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[AdapterMetadata] = None