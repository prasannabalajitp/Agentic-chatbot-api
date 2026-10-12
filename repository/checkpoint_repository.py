import logging
from typing import Callable, TypeVar

from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from database.mongodb import db
from core.constants import constants
from exceptions.database import DatabaseError, DatabaseConnectionError, DatabaseOperationError


logger = logging.getLogger(__name__)

T = TypeVar("T")


class CheckpointRepository:

    def __init__(self):
        self.checkpoints = db[constants.CHECKPOINTS]
        self.checkpoint_writes = db[constants.CHECKPOINTS_WRITES]

    def _handle_database_error(self, exc: Exception) -> None:
        if isinstance(exc, DatabaseError):
            raise exc

        logger.exception("Database operation failed.")

        if isinstance(exc, (ConnectionFailure, ServerSelectionTimeoutError)):
            raise DatabaseConnectionError() from exc

        raise DatabaseOperationError() from exc

    def _execute(self, operation: Callable[[], T]) -> T:
        try:
            return operation()
        except DatabaseError:
            raise
        except Exception as exc:
            self._handle_database_error(exc)

    def delete_thread_checkpoints(self, thread_id: str) -> None:
        self._execute(
            lambda: self.checkpoints.delete_many({
                constants.THREAD_ID: thread_id
            })
        )

        self._execute(
            lambda: self.checkpoint_writes.delete_many({
                constants.THREAD_ID: thread_id
            })
        )
