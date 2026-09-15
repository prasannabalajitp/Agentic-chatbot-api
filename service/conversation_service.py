from fastapi import HTTPException

from common.configurable import create_graph_config

from repository.user_repository import UserRepository
from repository.conversation_repository import ConversationRepository
from repository.file_repository import FileRepository

from service.chat_history_service import get_chat_history
from service.guardrail_service import GuardRailService
from service.title_service import TitleService
from models.response_model import ConversationResponse, ConversationListResponse
from core.constants import constants

import math
import logging

logger = logging.getLogger(__name__)

class ConversationService:

    def __init__(self, user_repository: UserRepository, conversation_repository: ConversationRepository, deep_agent, llm, title_llm, guardrail_service: GuardRailService, title_service: TitleService):
        self.deepagent = deep_agent
        self.llm = llm
        self.title_llm = title_llm
        self.user_repository = user_repository
        self.conversation_repository = conversation_repository
        self.guardrails = guardrail_service
        self.title_service = title_service
        self.file_repository = FileRepository()
    
    def create_conversation(self, user_id: str,   title: str = constants.DEFAULT_TITLE):
        if not self.user_repository.user_exists(user_id=user_id):
            raise HTTPException(
                status_code=404,
                detail=constants.USR_NOT_FOUND
            )

        result = self.conversation_repository.create_thread(
            user_id=user_id,
            title=title
        )

        data = {
            constants.THREAD_ID: result[constants.THREAD_ID],
            constants.USER_ID: result[constants.USER_ID],
            constants.TITLE: result[constants.TITLE],
            constants.CREATED_AT: str(result[constants.CREATED_AT])
        }
        return data

    def extract_chunk_content(self, chunk) -> str:
        logger.warning("CHUNK : %s", chunk)
        content = getattr(chunk, constants.CONTENT, constants.EMPTY_STRING)

        if isinstance(content, str):
            return content

        if isinstance(content, list):
            parts = []

            for item in content:
                if isinstance(item, str):
                    parts.append(item)

                elif isinstance(item, dict):
                    text = item.get(constants.TXT)

                    if text:
                        parts.append(text)

            return constants.EMPTY_STRING.join(parts)

        return constants.EMPTY_STRING
        
    
    def create_chat_config(self, user_id: str, thread_id: str):
        config  = create_graph_config(user_id, thread_id)
        config[constants.CONFIGURABLE][constants.UPLDED_FIELS] = (
            self.file_repository.get_thread_files(
                user_id=user_id,
                thread_id=thread_id,
            )
        )
        return config


    def get_messages(self, user_id: str,  thread_id: str):

        if not self.conversation_repository.validate_thread(user_id=user_id, thread_id=thread_id):
            raise HTTPException(
                status_code=404,
                detail=constants.CONVERSATION_NOT_FOUND
            )

        return get_chat_history(thread_id)

    def get_conversation(self, user_id: str, thread_id: str):
        if not self.conversation_repository.validate_thread(user_id=user_id, thread_id=thread_id):
            raise HTTPException(status_code=404, detail=constants.CONVERSATION_NOT_FOUND)
        conversation = self.conversation_repository.get_thread(thread_id=thread_id)

        if not conversation:
            raise HTTPException(
                status_code=404,
                detail=constants.CONVERSATION_NOT_FOUND
            )
        return conversation
    
    def get_conversation_details(self, user_id: str, page: int=1, limit: int=20):
        if page < 1:
            raise HTTPException(
                status_code=400,
                detail=constants.PAGE_EXCP
            )
        if limit < 1 or limit > 100:
            raise HTTPException(
                status_code=400,
                detail=constants.LMT_EXCP
            )
        
        if not self.user_repository.user_exists(user_id=user_id):
            raise HTTPException(
                status_code=404,
                detail=constants.USR_NOT_FOUND
            )
        
        skip = (page - 1) * limit
        conversations, total = self.conversation_repository.get_user_threads(user_id=user_id, skip=skip, limit=limit)

        conversation_items = [
            ConversationResponse(
                thread_id=conversation[constants.THREAD_ID],
                user_id=conversation[constants.USER_ID],
                title=conversation[constants.TITLE],
                message_count=conversation.get(constants.MSG_COUNT, 0),
                created_at=str(conversation[constants.CREATED_AT]),
                updated_at=str(conversation[constants.UPDATED_AT])
            )
            for conversation in conversations
        ]

        return ConversationListResponse(
            page=page,
            limit=limit,
            total=total,
            total_pages=math.ceil(total / limit),
            has_previous=page > 1,
            has_next=skip + limit < total,
            conversations=conversation_items
        )

    def delete_conversation(self, user_id: str,   thread_id: str):

        if not self.conversation_repository.validate_thread(user_id=user_id, thread_id=thread_id):
            raise HTTPException(
                status_code=404,
                detail=constants.CONVERSATION_NOT_FOUND
            )

        self.conversation_repository.delete_thread_checkpoints(thread_id=thread_id)
        self.conversation_repository.delete_thread_checkpoint_writes(thread_id)
        self.conversation_repository.delete_thread(thread_id)

        return {
            constants.MSG: constants.CONV_DEL_SUC
        }
    
    def clear_conversation_messages(self, user_id: str, thread_id: str):
        if not self.user_repository.user_exists(user_id):
            raise HTTPException(
                status_code=404,
                detail=constants.USR_NOT_FOUND
            )

        if not self.conversation_repository.validate_thread(user_id=user_id,    thread_id=thread_id):
            raise HTTPException(
                status_code=404,
                detail=constants.CONVERSATION_NOT_FOUND
            )

        self.conversation_repository.delete_thread_checkpoints(thread_id)
        self.conversation_repository.delete_thread_checkpoint_writes(thread_id)
        self.conversation_repository.reset_conversation(thread_id)

        conversation = self.conversation_repository.get_thread(thread_id)

        return {
            constants.THREAD_ID: conversation[constants.THREAD_ID],
            constants.USER_ID: conversation[constants.USER_ID],
            constants.TITLE: conversation[constants.TITLE],
            constants.MSG_COUNT: conversation[constants.MSG_COUNT],
            constants.UPDATED_AT: conversation[constants.UPDATED_AT],
            constants.MSG: constants.CONV_HST_SUC
        }
