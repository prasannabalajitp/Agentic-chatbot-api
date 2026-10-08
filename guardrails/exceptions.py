class ToolExecutionLimitError(Exception):
    """Raised when the maximum allowed tool-call count is exceeded."""

class ToolNotRegisteredError(Exception):
    """Raised when a tool is not registered in the tool registry."""

class ToolDisabledError(Exception):
    """Raised when a tool is registered but currently disabled."""

class ToolCallLimitExceededError(Exception):
    """Raised when a specific tool exceeds its allowed call count."""
