from database.mongodb import db
from core.constants import constants

class CheckpointRepository:

    def __init__(self):
        self.checkpoints = db[constants.CHECKPOINTS]
        self.checkpoint_writes = db[constants.CHECKPOINTS_WRITES]
    
    def delete_thread_checkpoints(self, thread_id: str):
        self.checkpoints.delete_many({
                constants.THREAD_ID: thread_id
            })

        self.checkpoint_writes.delete_many({
                constants.THREAD_ID: thread_id
            })
