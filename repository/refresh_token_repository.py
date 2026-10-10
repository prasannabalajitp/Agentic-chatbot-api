import logging
from datetime import datetime, timezone

from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from database.mongodb import refresh_tokens_collection
from core.constants import constants
from exceptions.database import DatabaseError, DatabaseConnectionError, DatabaseOperationError


logger = logging.getLogger(__name__)


class RefreshTokenRepository:
    def __init__(self):
        self.collection = refresh_tokens_collection

    def _handle_database_error(self, operation: str, exc: Exception) -> None:
        """Translate database failures into centralized exceptions."""

        if isinstance(exc, DatabaseError):
            raise

        if isinstance(exc, (ConnectionFailure, ServerSelectionTimeoutError)):
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

    def save_refresh_token(self, user_id: str, token_hash: str, expires_at: datetime):
        now = datetime.now(timezone.utc)

        document = {
            constants.USER_ID: user_id,
            constants.TKN_HSH: token_hash,
            constants.CREATED_AT: now,
            constants.UPDATED_AT: now,
            constants.EXP_AT: expires_at,
            constants.IS_REV: False,
        }

        self._execute(
            "save_refresh_token",
            lambda: self.collection.insert_one(document),
        )

        return document

    def get_refresh_tokens(self, user_id: str):
        return self._execute(
            "get_refresh_tokens",
            lambda: list(
                self.collection.find(
                    {constants.USER_ID: user_id},
                    {constants.ID: 0},
                ).sort(constants.CREATED_AT, -1)
            ),
        )

    def get_active_refresh_tokens(self, user_id: str):
        return self._execute(
            "get_active_refresh_tokens",
            lambda: list(
                self.collection.find(
                    {
                        constants.USER_ID: user_id,
                        constants.IS_REV: False,
                        constants.EXP_AT: {
                            constants.GT: datetime.now(timezone.utc),
                        },
                    },
                    {constants.ID: 0},
                )
            ),
        )

    def revoke_refresh_token(self, token_hash: str):
        return self._execute(
            "revoke_refresh_token",
            lambda: self.collection.update_one(
                {
                    constants.TKN_HSH: token_hash,
                    constants.IS_REV: False,
                },
                {
                    constants.SET: {
                        constants.IS_REV: True,
                    }
                },
            ),
        )

    def revoke_all_refresh_tokens(self, user_id: str):
        return self._execute(
            "revoke_all_refresh_tokens",
            lambda: self.collection.update_many(
                {
                    constants.USER_ID: user_id,
                    constants.IS_REV: False,
                    constants.EXP_AT: {
                        constants.GT: datetime.now(timezone.utc),
                    },
                },
                {
                    constants.SET: {
                        constants.IS_REV: True,
                    }
                },
            ),
        )

    def delete_expired_tokens(self):
        return self._execute(
            "delete_expired_tokens",
            lambda: self.collection.delete_many(
                {
                    constants.EXP_AT: {
                        constants.LT: datetime.now(timezone.utc),
                    }
                }
            ),
        )

    def get_refresh_token(self, token_hash: str):
        return self._execute(
            "get_refresh_token",
            lambda: self.collection.find_one(
                {
                    constants.TKN_HSH: token_hash,
                    constants.IS_REV: False,
                    constants.EXP_AT: {
                        constants.GT: datetime.now(timezone.utc),
                    },
                },
                {constants.ID: 0},
            ),
        )
