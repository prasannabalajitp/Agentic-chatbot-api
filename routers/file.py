from fastapi import APIRouter, Depends, UploadFile, File, Form
from dependencies import file_service, get_current_user
from core.constants import constants


router = APIRouter(prefix="/file", tags=[constants.FILE])


@router.post("")
async def create_file(thread_id: str = Form(...), file: UploadFile = File(...), current_user=Depends(get_current_user)):
    results = await file_service.create_file_service(
        user_id=current_user[constants.USER_ID], 
        thread_id=thread_id, 
        file=file
    )
    return results

@router.get("")
async def get_user_files(current_user=Depends(get_current_user)):
    return file_service.get_user_files(current_user[constants.USER_ID])


@router.get("/{file_id}")
async def get_file(file_id: str, current_user=Depends(get_current_user)):
    return file_service.get_file_service(
        user_id=current_user[constants.USER_ID],
        file_id=file_id
    )

@router.delete("/{file_id}")
async def delete_file(file_id: str, current_user=Depends(get_current_user)):
    return file_service.delete_file_service(
        user_id=current_user[constants.USER_ID],
        file_id=file_id
    )
