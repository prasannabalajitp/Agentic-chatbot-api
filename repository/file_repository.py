from datetime import datetime, timezone
from database.mongodb import file_collection
from core.constants import constants
from uuid import uuid4


class FileRepository:

    def __init__(self):
        self.collection = file_collection
    
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
            constants.UPDATED_AT: datetime.now(timezone.utc)
        }
        self.collection.insert_one(file)
        return file
    
    def get_file(self, user_id, file_id: str):
        return self.collection.find_one({
                constants.USER_ID: user_id,
                constants.FILE_ID: file_id
            },{
                constants.ID: 0
            })
    
    def get_user_files(self, user_id: str):
        return list(
            self.collection.find({
                constants.USER_ID: user_id
            },
            {
                constants.ID: 0
            }).sort(constants.CREATED_AT, -1)
        )
    
    def update_status(self, file_id: str, status: str):
        return self.collection.update_one(
            {
                constants.FILE_ID: file_id,
            },
            {
                constants.SET: {
                    constants.FILE_STATUS: status,
                    constants.UPDATED_AT: datetime.now(timezone.utc),
                }
            },
        )

    def delete_file(self, user_id: str, file_id: str):
        return self.collection.delete_one({
            constants.FILE_ID: file_id,
            constants.USER_ID: user_id}
        )
