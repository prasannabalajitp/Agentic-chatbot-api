import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from exceptions.base import ApplicationError
from exceptions.application import ResourceNotFoundError, ResourceConflictError, ValidationError, AuthenticationError, AuthorizationError
from exceptions.agent import AgentExecutionError, AgentConfigurationError, AgentTimeoutError
from exceptions.database import DatabaseError
from exceptions.external_service import ExternalServiceError, ExternalServiceTimeoutError, ExternalServiceUnavailableError
from exceptions.artifact import ArtifactNotFoundError

logger = logging.getLogger(__name__)


def get_status_code(exc: ApplicationError) -> int:
    """Map application exceptions to appropriate HTTP status codes."""

    if isinstance(exc, (ResourceNotFoundError, ArtifactNotFoundError)):
        return 404

    if isinstance(exc, ResourceConflictError):
        return 409

    if isinstance(exc, ValidationError):
        return 422

    if isinstance(exc, AuthenticationError):
        return 401

    if isinstance(exc, AuthorizationError):
        return 403

    if isinstance(exc, AgentTimeoutError):
        return 504

    if isinstance(exc, AgentConfigurationError):
        return 503

    if isinstance(exc, AgentExecutionError):
        return 500

    if isinstance(exc, DatabaseError):
        return 500

    if isinstance(exc, ExternalServiceTimeoutError):
        return 504

    if isinstance(exc, (ExternalServiceUnavailableError, ExternalServiceError)):
        return 502

    return 400


async def application_exception_handler(request: Request, exc: ApplicationError) -> JSONResponse:
    status_code = get_status_code(exc)

    logger.warning("Application error | code=%s | status=%s | path=%s", exc.code, status_code, request.url.path)

    message = exc.message

    if status_code >= 500:
        message = "The request could not be completed. Please try again."

    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": exc.code,
                "message": message,
            }
        },
    )


async def unexpected_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.error(
        "Unexpected application error | method=%s | path=%s",
        request.method,
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__),
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred.",
            }
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        ApplicationError,
        application_exception_handler,
    )
    app.add_exception_handler(
        Exception,
        unexpected_exception_handler,
    )
