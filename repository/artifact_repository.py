from datetime import datetime, timezone
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from database.mongodb import artifact_collection
from core.constants import constants
from exceptions.database import DatabaseConnectionError, DatabaseOperationError

import logging

logger = logging.getLogger(__name__)

class ArtifcatRepository:
    def __init__(self):
        self.collection = artifact_collection


    def create_artifact(self, artifact: dict):
        artifact[constants.CREATED_AT] = datetime.now(timezone.utc)
        try:
            result = self.collection.insert_one(artifact)
            return result.inserted_id
        except (ConnectionFailure, ServerSelectionTimeoutError) as exc:
            logger.exception("MongoDB connection failed while creating artifact")
            raise DatabaseConnectionError() from exc

        except Exception as exc:
            logger.exception("MongoDB failed to create artifact")
            raise DatabaseOperationError() from exc

    def get_artifact(self, artifact_id: str):
        try:
            return self.collection.find_one(
                {
                    constants.ARTIFACT_ID: artifact_id
                },
                {
                    constants.ID: 0
                }
            )

        except (ConnectionFailure, ServerSelectionTimeoutError) as exc:
            logger.exception("MongoDB connection failed while retrieving artifact")
            raise DatabaseConnectionError() from exc

        except Exception as exc:
            logger.exception("MongoDB failed to retrieve artifact")
            raise DatabaseOperationError() from exc
    
    def delete_artifact(self, artifact_id: str):
        try:
            return self.collection.delete_one(
                {
                    constants.ARTIFACT_ID: artifact_id
                }
            )

        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.exception("MongoDB connection failed while deleting artifact")
            raise DatabaseConnectionError() from e

        except Exception as e:
            logger.exception("MongoDB failed to delete artifact")
            raise DatabaseOperationError() from e
