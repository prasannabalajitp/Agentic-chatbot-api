from datetime import datetime, timezone
from database.mongodb import artifact_collection
from core.constants import constants


class ArtifcatRepository:
    def __init__(self):
        self.collection = artifact_collection


    def create_artifact(self, artifact: dict):
        artifact[constants.CREATED_AT] = datetime.now(timezone.utc)
        result = self.collection.insert_one(artifact)
        return result.inserted_id

    def get_artifact(self, artifact_id: str):
        return self.collection.find_one(
            {
                constants.ARTIFACT_ID: artifact_id
            },
            {
                constants.ID: 0
            }
        )
    
    def delete_artifact(self, artifact_id: str):
        return self.collection.delete_one(
            {
                constants.ARTIFACT_ID: artifact_id
            }
        )
