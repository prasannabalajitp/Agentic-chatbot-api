from exceptions.base import ApplicationError


class DatabaseError(ApplicationError):
    """Raised when a database operation fails."""

    def __init__(self,  message: str = "A database operation failed.",  *,  code: str = "DATABASE_ERROR") -> None:
        super().__init__(message, code=code)


class DatabaseConnectionError(DatabaseError):
    """Raised when a database connection fails."""

    def __init__(self,  message: str = "Unable to connect to the database.",    *,  code: str = "DATABASE_CONNECTION_ERROR") -> None:
        super().__init__(message, code=code)


class DatabaseOperationError(DatabaseError):
    """Raised when a database read, write, or delete operation fails."""

    def __init__(self,  message: str = "The database operation could not be completed.",    *,  code: str = "DATABASE_OPERATION_ERROR") -> None:
        super().__init__(message, code=code)
