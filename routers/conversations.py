from fastapi import APIRouter, Depends

from models.request_model import CreateConversationRequest, RenameConversatioRequest
from models.response_model import CreateConversationResponse

from dependencies import get_current_user

from core.constants import constants
from dependencies import conversation_service

router = APIRouter(prefix="/users", tags=[constants.CONVERSATIONS])

@router.post("/conversations")
async def create_conversation(request: CreateConversationRequest,current_user = Depends(get_current_user)):
    result = conversation_service.create_conversation(
        user_id = current_user["user_id"],
        title=request.title
    )
    return CreateConversationResponse(thread_id=result[constants.THREAD_ID], user_id=result[constants.USER_ID], title=result[constants.TITLE], created_at=result[constants.CREATED_AT])

@router.get("/conversations")
async def get_conversations(current_user = Depends(get_current_user), page: int=1, limit: int=20):
    return conversation_service.get_conversation_details(user_id=current_user["user_id"], page=page, limit=limit)


@router.delete("/conversations/{thread_id}")
async def delete_conversation(thread_id: str, current_user = Depends(get_current_user)):
    return conversation_service.delete_conversation(
        user_id=current_user["user_id"],
        thread_id=thread_id
    )

@router.delete("/conversations/{thread_id}/messages")
async def clear_conversation_messages(thread_id: str, current_user = Depends(get_current_user)):
    return conversation_service.clear_conversation_messages(
        user_id=current_user["user_id"],
        thread_id=thread_id
    )

@router.patch("/conversations/{thread_id}")
async def rename_conversation(thread_id: str, request: RenameConversatioRequest, current_user = Depends(get_current_user)):
    return conversation_service.rename_conversation(
        user_id=current_user["user_id"],
        thread_id=thread_id,
        title=request.title
    )
