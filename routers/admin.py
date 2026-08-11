from fastapi import APIRouter, Depends
from dependencies import admin_service, require_roles, get_current_user
from models.request_model import AdminUpdateRole
from core.constants import constants


router = APIRouter(prefix="/admin", tags=[constants.ADM], dependencies=[Depends(require_roles(constants.ADM))])

@router.get("/users")
async def get_users():
    return admin_service.get_all_users()

@router.get("/users/{user_id}")
async def get_specific_user(user_id: str):
    return admin_service.get_user(user_id)

@router.patch("/users/{user_id}/role")
async def update_role(user_id: str, req: AdminUpdateRole, current_user=Depends(get_current_user)):
    return admin_service.update_role(user_id, req.role, current_user[constants.USER_ID])

@router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    return admin_service.delete_user(user_id)

@router.get("/conversations")
async def get_all_conversation():
    return admin_service.get_all_conversations()

@router.delete("/conversations/{thread_id}")
async def delete_thread(thread_id: str):
    return admin_service.delete_conversation(thread_id)
