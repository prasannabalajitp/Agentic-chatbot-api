import mimetypes
from uuid import uuid4
from pathlib import Path

from core.constants import constants
from repository.artifact_repository import ArtifcatRepository

class ArtifactService:
    
    def __init__(self, artifact_repository: ArtifcatRepository):
        self.artifact_repository = artifact_repository

    def create_artifact(self, user_id: str, file_path: str, filename: str, content_type: str | None=None) -> dict:
        path = Path(file_path)

        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"Artifact file not found: {file_path}")

        artifact_id = str(uuid4())

        if not content_type:
            content_type = (mimetypes.guess_type(filename)[0] or "application/octet-stream")

        artifact = {
            constants.ARTIFACT_ID: artifact_id,
            constants.USER_ID: user_id,
            constants.FILE_NAME: filename,
            constants.FILE_PATH: str(path),
            constants.CONTENT_TYPE: content_type,
            constants.FILE_SIZE: path.stat().st_size,
        }

        self.artifact_repository.create_artifact(artifact)

        return {
            constants.ARTIFACT_ID: artifact_id,
            constants.FILE_NAME: filename,
            constants.CONTENT_TYPE: content_type,
            constants.FILE_SIZE: path.stat().st_size,
        }

    def get_artifact(self, artifact_id: str, user_id: str) -> dict | None:
        
        artifact = self.artifact_repository.get_artifact(artifact_id=artifact_id)
        
        if not artifact:
            return None

        if artifact[constants.USER_ID] != user_id:
            return None

        return artifact
