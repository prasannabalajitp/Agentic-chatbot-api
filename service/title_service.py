from langchain_core.messages import SystemMessage, HumanMessage
from fastapi import HTTPException

from common.prompt import TITLE_PROMPT
from core.constants import constants
from repository.user_repository import UserRepository
from repository.conversation_repository import ConversationRepository
import logging

logger = logging.getLogger(__name__)

class TitleService:

    def __init__(self, title_llm, user_repository: UserRepository, conversation_repository: ConversationRepository):
        self.title_llm = title_llm
        self.user_repository = user_repository
        self.conversation_repository = conversation_repository

    def generate_conversation_title(self, query: str):
            messages = [
                SystemMessage(content=TITLE_PROMPT),
                HumanMessage(
                    content=f"""
                User:
                {query}
                """
                        )
                    ]
            result = self.title_llm.invoke(messages)
            return result.content.strip()

    def rename_conversation(self, user_id: str, thread_id: str, title: str):
    
            if not self.user_repository.user_exists(user_id):
                raise HTTPException(
                    status_code=404,
                    detail=constants.USR_NOT_FOUND
                )
            if not self.conversation_repository.validate_thread(user_id=user_id, thread_id=thread_id):
                raise HTTPException(
                    status_code=404,
                    detail=constants.CONVERSATION_NOT_FOUND
                )
            
            title = title.strip()
    
            if not title:
                raise HTTPException(status_code=400, detail=constants.CONV_TITLE_NAME_EXCP)
            
            if len(title) > 100:
                raise HTTPException(status_code=400,    detail=constants.CONV_TITLE_EXCP)
            
            self. conversation_repository.update_thread_title(thread_id=thread_id, title= title)
    
            conversation = self.conversation_repository.get_thread(thread_id)
    
            return {
                constants.THREAD_ID: conversation[constants.THREAD_ID],
                constants.USER_ID: conversation[constants.USER_ID],
                constants.TITLE: conversation[constants.TITLE],
                constants.UPDATED_AT: conversation[constants.UPDATED_AT]
            }

    def rename_conversation_if_needed(self, user_id: str, thread_id: str, query: str):
            logger.warning("RENAME TASK STARTED | user=%s | thread=%s | query=%s", user_id, thread_id, query)
            try:
                if not self.conversation_repository.validate_thread(user_id=user_id, thread_id=thread_id):
                    return
                logger.warning("RENAME TASK: thread validated")
                conversation = self.conversation_repository.get_thread(thread_id)
                logger.warning("RENAME TASK: current title = %s", conversation[constants.TITLE])

                if conversation[constants.TITLE] != constants.DEFAULT_TITLE:
                    logger.warning("RENAME TASK: title already changed")
                    return
    
                logger.warning("RENAME TASK: generating title")
                title = self.generate_conversation_title(query=query)
    
                logger.warning("RENAME TASK: generated title = %s", title)
    
                self.conversation_repository.update_thread_title(thread_id=thread_id, title=title)
                logger.warning("RENAME TASK: title updated successfully")
            except Exception as ex:
                logger.warning("Failed to generate conversation title : %s",ex)
                return
