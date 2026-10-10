from exceptions.base import ApplicationError


class ArtifactError(ApplicationError):
    """Base exception for artifact-related operations."""

    def __init__(self,  message: str = "An artifact operation failed.", *,  code: str = "ARTIFACT_ERROR") -> None:
        super().__init__(message, code=code)


class ArtifactNotFoundError(ArtifactError):
    """Raised when an artifact does not exist or is inaccessible."""

    def __init__(self,  message: str = "The requested artifact was not found.", *,  code: str = "ARTIFACT_NOT_FOUND") -> None:
        super().__init__(message, code=code)


class ArtifactCreationError(ArtifactError):
    """Raised when artifact creation fails."""

    def __init__(self,  message: str = "Unable to create the artifact.",    *,  code: str = "ARTIFACT_CREATION_ERROR") -> None:
        super().__init__(message, code=code)


class ArtifactStorageError(ArtifactError):
    """Raised when artifact storage or retrieval fails."""

    def __init__(self,  message: str = "Unable to access artifact storage.",    *,  code: str = "ARTIFACT_STORAGE_ERROR") -> None:
        super().__init__(message, code=code)
