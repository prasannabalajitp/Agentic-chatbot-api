from fastapi import APIRouter, Depends

from dependencies import user_service, get_current_user
from models.request_model import LoginRequest, RefreshRequest, LogoutRequest
from core.constants import constants

router = APIRouter(prefix="/auth", tags=[constants.AUTH])

@router.post("/login")
async def login(request: LoginRequest):
    return user_service.login(request.user_id, request.password)

@router.post("/refresh")
async def refresh(request: RefreshRequest):
    return user_service.refresh(request.refresh_token)

@router.post("/logout")
async def logout(request: LogoutRequest):
    return user_service.logout(request.refresh_token)

@router.post("/logout-all")
async def logout_all(current_user=Depends(get_current_user)):
    return user_service.logout_all(current_user)
