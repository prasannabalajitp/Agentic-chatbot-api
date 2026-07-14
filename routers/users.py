from fastapi import APIRouter, Depends

from dependencies import get_current_user
from models.request_model import CreateUserRequest
from dependencies import user_service
from core.constants import constants

user_router = APIRouter(prefix="/users", tags=[constants.USERS])

@user_router.post("")
async def create_user(request: CreateUserRequest):
    return user_service.create_user(
        user_id=request.user_id,
        password=request.password,
        name=request.name,
        email=request.email
    )

@user_router.get("")
async def get_user(current_user = Depends(get_current_user)):
    user_id = current_user["user_id"]
    return user_service.get_user(user_id)


@user_router.delete("")
async def delete_user(current_user = Depends(get_current_user)):
    user_id = current_user["user_id"]
    return user_service.delete_user(user_id)
