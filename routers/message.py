from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse

from dependencies import get_current_user
from models.request_model import ChatRequest

from core.constants import constants
from dependencies import conversation_service

router = APIRouter(prefix="/conversations", tags=[constants.MESSAGES])


@router.post("/{thread_id}/messages")
async def create_message(background_tasks: BackgroundTasks,  thread_id: str, request: ChatRequest, current_user = Depends(get_current_user)):
    response = conversation_service.create_message(
        background_task=background_tasks,
        user_id=current_user["user_id"],
        thread_id=thread_id,
        query=request.query
    )

    return {
        "response": response
    }

@router.post("/{thread_id}/messagse/stream")
async def create_stream_message(thread_id: str, request: ChatRequest, current_user = Depends(get_current_user)):
    return StreamingResponse(
        conversation_service.stream_message(
            user_id=current_user["user_id"],
            thread_id=thread_id,
            query=request.query
        ),
        media_type=constants.MEDIA_TYPE,
        headers={
            constants.CACHE_CONTROL: constants.NO_CACHE,
            constants.CONN: constants.KEEP_ALIVE,
            constants.BUFFERING: constants.NO
        }
    )


@router.get("/{thread_id}/messages")
async def get_messages(thread_id: str, current_user = Depends(get_current_user)):
    return conversation_service.get_messages(
        user_id=current_user["user_id"],
        thread_id=thread_id
    )
