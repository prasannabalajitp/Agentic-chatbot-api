from fastapi import APIRouter, Depends, Query

from dependencies import get_current_user
from models.request_model import CreateUserRequest
from dependencies import user_service, usage_service
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
    user_id = current_user[constants.USER_ID]
    return user_service.get_user(user_id)


@user_router.get("/details")
async def get_user_details(current_user = Depends(get_current_user)):
    user_id = current_user[constants.USER_ID]
    return user_service.get_user(user_id)

@user_router.delete("")
async def delete_user(current_user = Depends(get_current_user)):
    user_id = current_user[constants.USER_ID]
    return user_service.delete_user(user_id)


@user_router.get("/usage")
async def get_user_usage(current_user = Depends(get_current_user)):
    user_id = current_user[constants.USER_ID]
    return usage_service.get_user_usage(user_id=user_id)

@user_router.get("/usage/tokens")
async def get_token_usage(period: str = Query(default="7d", pattern="^(7d|30d|90d)$"), current_user = Depends(get_current_user)):
    user_id = current_user[constants.USER_ID]
    return usage_service.get_token_usage(user_id=user_id, period=period)

@user_router.get("/usage/tools")
async def get_tool_usage(current_user=Depends(get_current_user)):
    user_id = current_user[constants.USER_ID]
    return usage_service.get_tool_usage(user_id=user_id)
