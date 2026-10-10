from exceptions.base import ApplicationError


class AgentExecutionError(ApplicationError):
    """Raised when agent execution fails."""

    def __init__(self,  message: str = "Agent execution failed.",   *,  code: str = "AGENT_EXECUTION_ERROR") -> None:
        super().__init__(message, code=code)


class AgentConfigurationError(ApplicationError):
    """Raised when agent configuration is invalid."""

    def __init__(self,  message: str = "Agent configuration is invalid.",   *,  code: str = "AGENT_CONFIGURATION_ERROR") -> None:
        super().__init__(message, code=code)


class AgentTimeoutError(ApplicationError):
    """Raised when agent execution exceeds its allowed time."""

    def __init__(self,  message: str = "Agent execution timed out.",    *,  code: str = "AGENT_TIMEOUT") -> None:
        super().__init__(message, code=code)
