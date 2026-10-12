import mimetypes
from uuid import uuid4
from pathlib import Path

from core.constants import constants
from repository.artifact_repository import ArtifcatRepository
from exceptions.artifact import ArtifactNotFoundError, ArtifactCreationError, ArtifactStorageError
from exceptions.database import DatabaseError

class ArtifactService:
    
    def __init__(self, artifact_repository: ArtifcatRepository):
        self.artifact_repository = artifact_repository

    def create_artifact(self, user_id: str, file_path: str, filename: str, content_type: str | None=None) -> dict:
        path = Path(file_path)

        if not path.exists() or not path.is_file():
            raise ArtifactNotFoundError("The artifact file does not exist.", code="ARTIFACT_FILE_NOT_FOUND")

        artifact_id = str(uuid4())

        if not content_type:
            content_type = (mimetypes.guess_type(filename)[0] or "application/octet-stream")

        try:
            file_size = path.stat().st_size

            artifact = {
                constants.ARTIFACT_ID: artifact_id,
                constants.USER_ID: user_id,
                constants.FILE_NAME: filename,
                constants.FILE_PATH: str(path),
                constants.CONTENT_TYPE: content_type,
                constants.FILE_SIZE: file_size,
            }
            self.artifact_repository.create_artifact(artifact)

        except DatabaseError:
            raise

        except OSError as e:
            raise ArtifactStorageError("Unable to access artifact storage.") from e

        except Exception as e:
            raise ArtifactCreationError() from e

        return {
            constants.ARTIFACT_ID: artifact_id,
            constants.FILE_NAME: filename,
            constants.CONTENT_TYPE: content_type,
            constants.FILE_SIZE: path.stat().st_size,
        }

    def get_artifact(self, artifact_id: str, user_id: str) -> dict | None:
        
        try:
            artifact = self.artifact_repository.get_artifact(artifact_id=artifact_id)

        except DatabaseError:
            raise

        except Exception as e:
            raise ArtifactStorageError("Unable to retrieve the artifact.") from e
        
        if not artifact:
            return None

        if artifact[constants.USER_ID] != user_id:
            return None

        return artifact
