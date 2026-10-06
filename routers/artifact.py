from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

from dependencies import artifact_service, get_current_user
from core.constants import constants

router = APIRouter(prefix="/artifacts", tags=[constants.ARTIFACTS])


@router.get("/{artifact_id}/download")
async def download_artifact(artifact_id: str, current_user=Depends(get_current_user)):
    artifact = artifact_service.get_artifact(artifact_id=artifact_id, user_id=current_user[constants.USER_ID])

    if not artifact:
        raise HTTPException(status_code=404, detail=constants.ARTIFACT_NOT_FOUND)

    file_path = Path(artifact[constants.FILE_PATH])

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail=constants.ARTIFACT_NOT_FOUND)

    return FileResponse(
        path=str(file_path),
        filename=artifact[constants.FILE_NAME],
        media_type=artifact[constants.CONTENT_TYPE]
    )
