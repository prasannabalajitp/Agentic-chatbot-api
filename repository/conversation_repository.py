from datetime import datetime, timezone
from uuid import uuid4

from database.mongodb import threads_collection, checkpoints_collection, checkpoint_writes_collection
from core.constants import constants


class ConversationRepository:

    def __init__(self):
        self.collections = threads_collection
        self.checkpoints = checkpoints_collection
        self.checkpoint_writes = checkpoint_writes_collection

    def create_thread(self, user_id: str, title: str = constants.DEFAULT_TITLE):
        thread = {
            constants.THREAD_ID: str(uuid4()),
            constants.USER_ID: user_id,
            constants.TITLE: title,
            constants.MSG_COUNT: 0,
            constants.CREATED_AT: datetime.now(timezone.utc),
            constants.UPDATED_AT: datetime.now(timezone.utc),
            constants.LST_MSG_AT: datetime.now(timezone.utc)
        }

        self.collections.insert_one(thread)

        return thread

    def get_thread(self, thread_id: str):
        return self.collections.find_one(
            {constants.THREAD_ID: thread_id},
            {constants.ID: 0}
        )

    def validate_thread(self, user_id: str,   thread_id: str) -> bool:
        return (
            self.collections.count_documents(
                {
                    constants.USER_ID: user_id,
                    constants.THREAD_ID: thread_id
                },
                limit=1
            )
            > 0
        )
    
    def get_all_threads(self):
        return list(
            self.collections.find({}, {"_id": 0})
        )

    def get_user_threads(self, user_id: str, skip: int, limit: int):
        conversations = list(self.collections.find(
                {constants.USER_ID: user_id},
                {constants.ID: 0}
            ).sort(constants.UPDATED_AT, -1)
            .skip(skip)
            .limit(limit)
        )
        total = self.collections.count_documents(
            {constants.USER_ID: user_id}
        )

        return conversations, total

    def update_conversation_activity(self, thread_id: str):
        self.collections.update_one(
            {
                constants.THREAD_ID: thread_id
            },
            {
                constants.SET: {
                    constants.UPDATED_AT: datetime.now(timezone.utc),
                    constants.LST_MSG_AT: datetime.now(timezone.utc)
                },
                constants.INC:{
                    constants.MSG_COUNT: 2
                }
            }
        )

    def update_thread_title(self, thread_id: str,   title: str):
        self.collections.update_one(
            {
                constants.THREAD_ID: thread_id
            },
            {
                constants.SET: {
                    constants.TITLE: title,
                    constants.UPDATED_AT: datetime.now(timezone.utc)
                }
            }
        )

    def delete_thread(self, thread_id: str):
        return self.collections.delete_one(
            {
                constants.THREAD_ID: thread_id
            }
        )
    
    def delete_user_threads(self, user_id:str):
        return self.collections.delete_many(
            {constants.USER_ID: user_id}
        )
    
    def reset_conversation(self, thread_id: str):
        now = datetime.now(timezone.utc)
        self.collections.update_one(
            {
                constants.THREAD_ID: thread_id
            },
            {
                constants.SET: {
                    constants.TITLE: constants.DEFAULT_TITLE,
                    constants.MSG_COUNT: 0,
                    constants.UPDATED_AT: now,
                    constants.LST_MSG_AT: None
                }
            }
        )

    def delete_thread_checkpoints(self, thread_id: str):
        self.checkpoints.delete_many({
            constants.THREAD_ID: thread_id
        })

    def delete_thread_checkpoint_writes(self, thread_id: str):
        self.checkpoint_writes.delete_many({
            constants.THREAD_ID: thread_id
        })
