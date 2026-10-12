from core.constants import constants
from exceptions.base import ApplicationError

class ToolError(ApplicationError):
    """Base exception for tool execution and policy failures."""

    def __init__(self,  message: str,   *,  code: str = "TOOL_ERROR") -> None:
        super().__init__(message, code=code)


class ToolNotRegisteredError(ToolError):
    """Raised when a requested tool is absent from the registry."""

    def __init__(self,  message: str = "The requested tool is not registered.", *,  code: str = "TOOL_NOT_REGISTERED") -> None:
        super().__init__(message, code=code)


class ToolDisabledError(ToolError):
    """Raised when a registered tool is disabled."""

    def __init__(self,  message: str = "The requested tool is disabled.",   *,  code: str = "TOOL_DISABLED") -> None:
        super().__init__(message, code=code)


class ToolExecutionLimitError(ToolError):
    """Raised when the overall tool execution limit is exceeded."""

    def __init__(self,  message: str = "The maximum tool execution limit was exceeded.",    *,  code: str = "TOOL_EXECUTION_LIMIT_EXCEEDED") -> None:
        super().__init__(message, code=code)


class ToolCallLimitExceededError(ToolError):
    """Raised when an individual tool exceeds its execution limit."""

    def __init__(self,  message: str = "The tool execution limit was exceeded.",    *,  code: str = "TOOL_CALL_LIMIT_EXCEEDED") -> None:
        super().__init__(message, code=code)


class ManyToolCallException(ToolError):
    def __init__(self, message:str = constants.MNY_TOOL_CALL, *, code = "TOOL_ERROR"):
        super().__init__(message, code=code)
