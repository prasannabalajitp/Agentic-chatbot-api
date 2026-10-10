class ApplicationError(Exception):
    """Base class for expected application-level exceptions."""

    def __init__(self,  message: str, *, code: str = "APPLICATION_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.code = code
