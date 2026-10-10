import logging
from datetime import datetime, timezone
from typing import Callable, TypeVar

from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from database.mongodb import users_collection
from core.constants import constants
from exceptions.database import DatabaseError, DatabaseConnectionError, DatabaseOperationError


logger = logging.getLogger(__name__)

T = TypeVar("T")


class UserRepository:

    def __init__(self):
        self.collection = users_collection

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

    def create_user(self, user_id: str, password_hash: str, name: str | None = None, email: str | None = None, role: str | None = None):
        document = {
            constants.USER_ID: user_id,
            constants.NAME: name,
            constants.EMAIL: email,
            constants.HASHED_PWD: password_hash,
            constants.ROLE: role,
            constants.CREATED_AT: datetime.now(timezone.utc),
        }

        self._execute(
            lambda: self.collection.insert_one(document)
        )
        return document

    def get_user(self, user_id: str):
        return self._execute(
            lambda: self.collection.find_one(
                {constants.USER_ID: user_id},
                {constants.ID: 0},
            )
        )

    def user_exists(self, user_id: str) -> bool:
        return self._execute(
            lambda: (
                self.collection.count_documents(
                    {constants.USER_ID: user_id},
                    limit=1,
                ) > 0
            )
        )

    def get_all_users(self):
        return self._execute(
            lambda: list(
                self.collection.find(
                    {},
                    {constants.ID: 0},
                )
            )
        )

    def delete_user(self, user_id: str):
        return self._execute(
            lambda: self.collection.delete_one(
                {constants.USER_ID: user_id}
            )
        )

    def update_role(self, user_id: str, role: str):
        result = self._execute(
            lambda: self.collection.update_one(
                {constants.USER_ID: user_id},
                {
                    constants.SET: {
                        constants.ROLE: role
                    }
                },
            )
        )

        return {
            constants.MATCHED: result.matched_count,
            constants.MODIFIED: result.modified_count,
        }
