import logging
from datetime import datetime, timezone
from uuid import uuid4

from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from database.mongodb import threads_collection, checkpoints_collection, checkpoint_writes_collection
from exceptions.database import DatabaseError, DatabaseConnectionError, DatabaseOperationError
from core.constants import constants


logger = logging.getLogger(__name__)


class ConversationRepository:
    def __init__(self):
        self.collections = threads_collection
        self.checkpoints = checkpoints_collection
        self.checkpoint_writes = checkpoint_writes_collection

    def _handle_database_error(self, operation: str, exc: Exception,) -> None:
        """Translate database failures into centralized exceptions."""

        if isinstance(exc, DatabaseError):
            raise

        if isinstance(exc,(ConnectionFailure, ServerSelectionTimeoutError)):
            logger.exception("Database connection failure | operation=%s", operation)
            raise DatabaseConnectionError() from exc

        logger.exception("Database operation failed | operation=%s", operation)
        raise DatabaseOperationError() from exc

    def _execute(self, operation: str, callback):
        """Execute a database operation with centralized error handling."""

        try:
            return callback()
        except Exception as exc:
            self._handle_database_error(operation, exc)

    def create_thread(self, user_id: str, title: str = constants.DEFAULT_TITLE,):
        now = datetime.now(timezone.utc)

        thread = {
            constants.THREAD_ID: str(uuid4()),
            constants.USER_ID: user_id,
            constants.TITLE: title,
            constants.MSG_COUNT: 0,
            constants.CREATED_AT: now,
            constants.UPDATED_AT: now,
            constants.LST_MSG_AT: now,
        }

        self._execute("create_thread", lambda: self.collections.insert_one(thread))

        return thread

    def get_thread(self, thread_id: str):
        return self._execute(
            "get_thread",
            lambda: self.collections.find_one(
                {constants.THREAD_ID: thread_id},
                {constants.ID: 0},
            ),
        )

    def validate_thread(self, user_id: str, thread_id: str) -> bool:
        count = self._execute(
            "validate_thread",
            lambda: self.collections.count_documents(
                {
                    constants.USER_ID: user_id,
                    constants.THREAD_ID: thread_id,
                },
                limit=1,
            ),
        )

        return count > 0

    def get_all_threads(self):
        return self._execute(
            "get_all_threads",
            lambda: list(
                self.collections.find(
                    {},
                    {constants.ID: 0},
                )
            ),
        )

    def get_user_threads(self, user_id: str, skip: int, limit: int,):
        conversations = self._execute(
            "get_user_threads",
            lambda: list(
                self.collections.find(
                    {constants.USER_ID: user_id},
                    {constants.ID: 0},
                )
                .sort(constants.UPDATED_AT, -1)
                .skip(skip)
                .limit(limit)
            ),
        )

        total = self._execute(
            "count_user_threads",
            lambda: self.collections.count_documents(
                {constants.USER_ID: user_id}
            ),
        )

        return conversations, total

    def update_conversation_activity(self, thread_id: str):
        now = datetime.now(timezone.utc)

        return self._execute(
            "update_conversation_activity",
            lambda: self.collections.update_one(
                {constants.THREAD_ID: thread_id},
                {
                    constants.SET: {
                        constants.UPDATED_AT: now,
                        constants.LST_MSG_AT: now,
                    },
                    constants.INC: {
                        constants.MSG_COUNT: 2,
                    },
                },
            ),
        )

    def update_thread_title(self, thread_id: str, title: str):
        return self._execute(
            "update_thread_title",
            lambda: self.collections.update_one(
                {constants.THREAD_ID: thread_id},
                {
                    constants.SET: {
                        constants.TITLE: title,
                        constants.UPDATED_AT: datetime.now(timezone.utc),
                    }
                },
            ),
        )

    def delete_thread(self, thread_id: str):
        return self._execute(
            "delete_thread",
            lambda: self.collections.delete_one(
                {constants.THREAD_ID: thread_id}
            ),
        )

    def delete_user_threads(self, user_id: str):
        return self._execute(
            "delete_user_threads",
            lambda: self.collections.delete_many(
                {constants.USER_ID: user_id}
            ),
        )

    def reset_conversation(self, thread_id: str):
        now = datetime.now(timezone.utc)

        return self._execute(
            "reset_conversation",
            lambda: self.collections.update_one(
                {constants.THREAD_ID: thread_id},
                {
                    constants.SET: {
                        constants.TITLE: constants.DEFAULT_TITLE,
                        constants.MSG_COUNT: 0,
                        constants.UPDATED_AT: now,
                        constants.LST_MSG_AT: None,
                    }
                },
            ),
        )

    def delete_thread_checkpoints(self, thread_id: str):
        return self._execute(
            "delete_thread_checkpoints",
            lambda: self.checkpoints.delete_many(
                {constants.THREAD_ID: thread_id}
            ),
        )

    def delete_thread_checkpoint_writes(self, thread_id: str):
        return self._execute(
            "delete_thread_checkpoint_writes",
            lambda: self.checkpoint_writes.delete_many(
                {constants.THREAD_ID: thread_id}
            ),
        )
