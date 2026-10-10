from exceptions.base import ApplicationError


class ExternalServiceError(ApplicationError):
    """Raised when an external service fails."""

    def __init__(self,  message: str = "An external service request failed.",   *,  code: str = "EXTERNAL_SERVICE_ERROR") -> None:
        super().__init__(message, code=code)


class ExternalServiceTimeoutError(ExternalServiceError):
    """Raised when an external service request times out."""

    def __init__(self,  message: str = "The external service request timed out.",   *,  code: str = "EXTERNAL_SERVICE_TIMEOUT") -> None:
        super().__init__(message, code=code)


class ExternalServiceUnavailableError(ExternalServiceError):
    """Raised when an external service is unavailable."""

    def __init__(self,  message: str = "The external service is currently unavailable.",    *,  code: str = "EXTERNAL_SERVICE_UNAVAILABLE") -> None:
        super().__init__(message, code=code)
