from fastapi import APIRouter

from dependencies import user_service
from models.request_model import LoginRequest
from core.constants import constants

router = APIRouter(prefix="/auth", tags=[constants.AUTH])

@router.post("/login")
async def login(request: LoginRequest):
    return user_service.login(request.user_id, request.password)
