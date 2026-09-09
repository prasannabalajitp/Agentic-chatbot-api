from fastapi import HTTPException, BackgroundTasks
from langchain_core.messages import HumanMessage, SystemMessage
from datetime import datetime, timezone

from common.configurable import create_graph_config
from common.prompt import TITLE_PROMPT
from common.sse import sse_event

from repository.user_repository import UserRepository
from repository.conversation_repository import ConversationRepository
from repository.file_repository import FileRepository

from service.chat_history_service import get_chat_history
from service.guardrail_service import GuardRailService
from models.response_model import ConversationResponse, ConversationListResponse
from core.constants import constants
from core.config import settings

import math
import json
import logging

logger = logging.getLogger(__name__)

class ConversationService:

    def __init__(self, user_repository: UserRepository, conversation_repository: ConversationRepository, deep_agent, llm, title_llm, guardrail_service: GuardRailService):
        self.deepagent = deep_agent
        self.llm = llm
        self.title_llm = title_llm
        self.user_repository = user_repository
        self.conversation_repository = conversation_repository
        self.guardrails = guardrail_service
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

            self.conversation_repository.update_thread_title(thread_id=thread_id,title=title)
            logger.warning("RENAME TASK: title updated successfully")

        except Exception as ex:
            logger.warning("Failed to generate conversation title : %s",ex)
            return
        
    
    def create_chat_config(self, user_id: str, thread_id: str):
        config  = create_graph_config(user_id, thread_id)
        config[constants.CONFIGURABLE][constants.UPLDED_FIELS] = (
            self.file_repository.get_thread_files(
                user_id=user_id,
                thread_id=thread_id,
            )
        )
        return config

    def create_message(self, background_task: BackgroundTasks, user_id: str, thread_id: str, query: str):
        if not self.conversation_repository.validate_thread(user_id=user_id, thread_id=thread_id):
            raise HTTPException(
                status_code=404,
                detail=constants.CONVERSATION_NOT_FOUND
            )
        
        self.guardrails.validate_prompt(query)
        config = self.create_chat_config(user_id, thread_id)
        input_messages = [HumanMessage(content=query)]
        logger.error("RAW INPUT TO INVOKE: %s", [(m.type, m.id, m.content) for m in input_messages])
        logger.error("CONFIG : %s", config)
        result = self.deepagent.invoke({
                constants.MESSAGES: input_messages
            },
            config=config
        )

        logger.warning("=============================")
        logger.warning(result)
        response = result[constants.MESSAGES][-1].content
        response = self.guardrails.validate_response(response)
        self.conversation_repository.update_conversation_activity(thread_id=thread_id)

        background_task.add_task(self.rename_conversation_if_needed, user_id, thread_id, query)
        return {
            constants.RESPONSE: response,
            constants.CITATIONS: result.get(constants.CITATIONS, []),
        }
    
    async def stream_message(self, background_task: BackgroundTasks, user_id: str, thread_id: str, query: str):
            if not self.conversation_repository.validate_thread(user_id=user_id, thread_id=thread_id):
                raise HTTPException(
                    status_code=404,
                    detail=constants.CONVERSATION_NOT_FOUND
                )
            
            try:
                self.guardrails.validate_prompt(query)
            except HTTPException as e:
                yield sse_event(
                    constants.ERR,
                    {
                        constants.MSG: e.detail
                    }
                )
    
                return
        
            config = self.create_chat_config(user_id, thread_id)
            yield sse_event(constants.CHART_STRT, {
                    constants.USER_ID: user_id,
                    constants.THREAD_ID: thread_id,
                    constants.QUERY: query
                })
            
            yield sse_event(
                constants.CHART_MDL_STRT,
                {
                    constants.MDL: settings.MODEL_NAME
                }
            )
            
            final_response = constants.EMPTY_STRING
            final_citations = []
            tool_call_count = 0
    
            try:
                current_model_chunks = []
                current_model_has_tool_call = False
                model_generation = 0
                async for event in self.deepagent.astream_events(
                    {
                        constants.MESSAGES: [
                            HumanMessage(content=query)
                        ]
                    },
                    config=config,
                    version=constants.V2
                ):
                    event_name = event.get(constants.EVENT)
                    event_name_value = event.get(constants.NAME)

                    logger.warning("DEEPAGENT EVENT: %s | NAME: %s | DATA: %r", event_name, event_name_value, event.get(constants.DATA),)
                    if event_name == constants.ON_CHAT_MDL_STRT:
                        model_generation += 1
                        current_model_chunks = []
                        current_model_has_tool_call = False

                        yield sse_event(
                            constants.CHART_MDL_STRT,
                            {constants.MDL: settings.MODEL_NAME},
                        )

                    elif event_name == constants.ON_CHAT_MDL_STRM:
                        chunk = event[constants.DATA].get(constants.CHUNK)
                        content = self.extract_chunk_content(chunk)
                        logger.info("CONTENT : %s", content)
                        if content:
                            current_model_chunks.append(content)

                            yield sse_event(
                                constants.LLM_CHUNK,
                                {
                                    constants.CONTENT: content
                                }
                            )
                    elif event_name == constants.ON_CHAT_MDL_END:
                        output = event[constants.DATA].get(constants.OUTPUT)
                        tool_calls = getattr(output, constants.TOOL_CALLS, []) or []
                        if tool_calls:
                            current_model_has_tool_call = True

                        if not tool_calls:
                            response_text = constants.EMPTY_STRING.join(current_model_chunks)
                            if response_text:
                                final_response += response_text

                                yield sse_event(
                                    constants.LLM_CHUNK,
                                    {constants.CONTENT: response_text},
                                )
                        yield sse_event(
                            constants.CHART_MDL_END,
                            {constants.MDL: settings.MODEL_NAME},
                        )
                    elif event_name == constants.ON_TOOL_START:
                        tool_call_count += 1
    
                        tool_name = event_name_value
                        self.guardrails.validate_tool(
                            tool_name=tool_name,
                            tool_calls=tool_call_count
                        )

                        yield sse_event(
                            constants.TOOL_CALL,
                            {
                                constants.TOOL: tool_name,
                                constants.ARGS: event[constants.DATA].get(
                                    constants.INPUT,
                                    {}
                                )
                            }
                        )
    
                    elif event_name == constants.ON_TOOL_END:
                        tool_output = event[constants.DATA].get(constants.OUTPUT)

                        logger.warning("TOOL OUTPUT: %r", tool_output)
                        if tool_output:
                            tool_name = getattr(tool_output, constants.NAME, event_name_value)

                            tool_id = getattr(tool_output, constants.TOOL_ID, constants.EMPTY_STRING)

                            tool_content = getattr(tool_output, constants.CONTENT, str(tool_output))

                            if isinstance(tool_content, str):

                                try:
                                    tool_result = json.loads(tool_content)

                                    citations = tool_result.get(constants.CITATIONS, [])

                                    if citations:
                                        final_citations.extend(citations)

                                        logger.warning("CITATIONS FOUND: %s", citations)

                                except (json.JSONDecodeError, TypeError):
                                    logger.warning("Tool output is not JSON: %r",tool_content)
                                    
                            yield sse_event(
                                constants.TOOL_RESP,
                                {
                                    constants.TOOL: tool_name,
                                    constants.TOOL_ID: tool_id,
                                    constants.RESPONSE: tool_content,
                                }
                            )
            except Exception as e:
                yield sse_event(
                    constants.ERR,
                    {
                        constants.TYPE: type(e).__name__,
                        constants.MSG: str(e)
                    },
                )
                return
            
            self.conversation_repository.update_conversation_activity(thread_id=thread_id)
            yield sse_event(
                constants.CONV_ACTY,
                {
                    constants.THREAD_ID: thread_id
                }
            )
            conversation = self.conversation_repository.get_thread(thread_id=thread_id)
            logger.warning("CONVERSATION : %s", conversation)
    
            background_task.add_task(
                self.rename_conversation_if_needed,
                user_id,
                thread_id,
                query,
            )
            
            yield sse_event(
                constants.CHART_MDL_END,
                {
                    constants.MDL: settings.MODEL_NAME
                }
            )
    
            try:
                final_response = self.guardrails.validate_response(
                    final_response
                )
            except Exception as e:
                yield sse_event(
                    constants.ERR,
                    {
                        constants.MSG: str(e)
                    }
                )
    
                return
    
    
            yield sse_event(
                constants.DONE,
                {
                    constants.THREAD_ID: thread_id,
                    constants.RESPONSE: final_response,
                    constants.CITATIONS: final_citations,
                    constants.TS: str(datetime.now(timezone.utc).isoformat()),
                    constants.MSG_COUNT: conversation[constants.MSG_COUNT] if conversation[constants.MSG_COUNT] else 0,
                    constants.FNSH_RESON: constants.CMPLTD,
                }
            )


    def get_messages(self, user_id: str,  thread_id: str):

        if not self.conversation_repository.validate_thread(
            user_id=user_id,
            thread_id=thread_id
        ):
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

        if not self.conversation_repository.validate_thread(
            user_id=user_id,
            thread_id=thread_id
        ):
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
