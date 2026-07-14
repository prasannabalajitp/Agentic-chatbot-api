from datetime import datetime, timezone
from database.mongodb import users_collection
from core.constants import constants

class UserRepository:

    def __init__(self):
        self.collection = users_collection

    def create_user(self, user_id: str, password_hash: str, name: str | None = None,    email: str | None = None):
        document = {
            constants.USER_ID: user_id,
            constants.NAME: name,
            constants.EMAIL: email,
            constants.HASHED_PWD: password_hash,
            constants.CREATED_AT: datetime.now(timezone.utc)
        }

        self.collection.insert_one(document)
        return document

    def get_user(self, user_id: str):
        return self.collection.find_one(
            {constants.USER_ID: user_id},
            {constants.ID: 0}
        )

    def user_exists(self, user_id: str) -> bool:
        return (
            self.collection.count_documents(
                {constants.USER_ID: user_id},
                limit=1
            )
            > 0
        )

    def get_all_users(self):
        return list(
            self.collection.find(
                {},
                {constants.ID: 0}
            )
        )

    def delete_user(self, user_id: str):
        return self.collection.delete_one(
            {constants.USER_ID: user_id}
        )
