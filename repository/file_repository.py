from datetime import datetime, timezone
from uuid import uuid4

from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from database.mongodb import file_collection
from core.constants import constants
from exceptions.database import DatabaseError, DatabaseConnectionError, DatabaseOperationError


class FileRepository:
    def __init__(self):
        self.collection = file_collection

    def _handle_database_error(self, operation: str, exc: Exception) -> None:
        """Translate database failures into centralized exceptions."""

        if isinstance(exc, DatabaseError):
            raise

        if isinstance(exc, (ConnectionFailure, ServerSelectionTimeoutError)):
            raise DatabaseConnectionError() from exc

        raise DatabaseOperationError() from exc

    def _execute(self, operation: str, callback):
        """Execute a database operation with centralized error handling."""

        try:
            return callback()
        except Exception as exc:
            self._handle_database_error(operation, exc)

    def create_file(self, user_id, thread_id, file_name, content_type, file_size):
        file = {
            constants.FILE_ID: str(uuid4()),
            constants.USER_ID: user_id,
            constants.THREAD_ID: thread_id,
            constants.FILE_NAME: file_name,
            constants.CONTENT_TYPE: content_type,
            constants.SIZE: file_size,
            constants.FILE_STATUS: constants.UPLOADED,
            constants.CREATED_AT: datetime.now(timezone.utc),
            constants.UPDATED_AT: datetime.now(timezone.utc),
        }

        self._execute("create_file", lambda: self.collection.insert_one(file))

        return file

    def get_file(self, user_id, file_id: str):
        return self._execute(
            "get_file",
            lambda: self.collection.find_one(
                {
                    constants.USER_ID: user_id,
                    constants.FILE_ID: file_id,
                },
                {
                    constants.ID: 0,
                },
            ),
        )

    def get_user_files(self, user_id: str):
        return self._execute(
            "get_user_files",
            lambda: list(
                self.collection.find(
                    {
                        constants.USER_ID: user_id,
                    },
                    {
                        constants.ID: 0,
                    },
                ).sort(constants.CREATED_AT, -1)
            ),
        )

    def update_status(self, file_id: str, status: str):
        return self._execute(
            "update_status",
            lambda: self.collection.update_one(
                {
                    constants.FILE_ID: file_id,
                },
                {
                    constants.SET: {
                        constants.FILE_STATUS: status,
                        constants.UPDATED_AT: datetime.now(timezone.utc),
                    },
                },
            ),
        )

    def delete_file(self, user_id: str, file_id: str):
        return self._execute(
            "delete_file",
            lambda: self.collection.delete_one(
                {
                    constants.FILE_ID: file_id,
                    constants.USER_ID: user_id,
                },
            ),
        )

    def has_thread_files(self, user_id: str, thread_id: str) -> bool:
        count = self._execute(
            "has_thread_files",
            lambda: self.collection.count_documents(
                {
                    constants.USER_ID: user_id,
                    constants.THREAD_ID: thread_id,
                },
                limit=1,
            ),
        )

        return count > 0

    def get_thread_files(self, user_id: str, thread_id: str):
        return self._execute(
            "get_thread_files",
            lambda: list(
                self.collection.find(
                    {
                        constants.USER_ID: user_id,
                        constants.THREAD_ID: thread_id,
                    },
                    {
                        constants.ID: 0,
                    },
                ).sort(constants.CREATED_AT, -1)
            ),
        )
