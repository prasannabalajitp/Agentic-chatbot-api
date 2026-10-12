from exceptions.base import ApplicationError

class ResourceNotFoundError(ApplicationError):
    """Raised when a requested resource does not exist."""

    def __init__(self,  message: str = "The requested resource was not found.", *,  code: str = "RESOURCE_NOT_FOUND") -> None:
        super().__init__(message, code=code)


class ResourceConflictError(ApplicationError):
    """Raised when an operation conflicts with the current state."""

    def __init__(self,  message: str = "The requested operation conflicts with the current state.", *,  code: str = "RESOURCE_CONFLICT") -> None:
        super().__init__(message, code=code)


class ValidationError(ApplicationError):
    """Raised when application-level input validation fails."""

    def __init__(self,  message: str = "The supplied input is invalid.",    *,  code: str = "VALIDATION_ERROR") -> None:
        super().__init__(message, code=code)


class AuthenticationError(ApplicationError):
    """Raised when authentication fails."""

    def __init__(self,  message: str = "Authentication failed.",    *,  code: str = "AUTHENTICATION_ERROR") -> None:
        super().__init__(message, code=code)


class AuthorizationError(ApplicationError):
    """Raised when a user lacks permission to perform an operation."""

    def __init__(self,  message: str = "You are not authorized to perform this operation.", *,  code: str = "AUTHORIZATION_ERROR") -> None:
        super().__init__(message, code=code)

