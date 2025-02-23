"""Exceptions for CrewAI adapters."""

class AdapterError(Exception):
    """Base exception for adapter-related errors."""
    pass

class ConfigurationError(AdapterError):
    """Raised when adapter configuration is invalid."""
    pass

class ExecutionError(AdapterError):
    """Raised when adapter execution fails."""
    pass

class ValidationError(AdapterError):
    """Raised when adapter validation fails."""
    pass
