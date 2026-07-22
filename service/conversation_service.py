from fastapi import HTTPException, BackgroundTasks
from langchain_core.messages import HumanMessage, SystemMessage
from datetime import datetime, timezone

from common.configurable import create_graph_config
from common.prompt import TITLE_PROMPT
from common.sse import sse_event

from repository.user_repository import UserRepository
from repository.conversation_repository import ConversationRepository

from service.chat_history_service import get_chat_history
from models.response_model import ConversationResponse, ConversationListResponse
from core.constants import constants
from core.config import settings

import math, json

class ConversationService:

    def __init__(self, user_repository: UserRepository, conversation_repository: ConversationRepository, graph, llm):
        self.graph = graph
        self.llm = llm
        self.user_repository = user_repository
        self.conversation_repository = conversation_repository
    
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
    
    def rename_conversation_if_needed(self, thread_id: str, query: str):

        try:
            conversation = self.conversation_repository.get_thread(thread_id)
            if conversation[constants.TITLE] != constants.DEFAULT_TITLE:
                return

            title = self.generate_conversation_title(query=query)

            self.conversation_repository.update_thread_title(
                thread_id=thread_id,
                title=title
            )
        except Exception:
            raise HTTPException(status_code=500, detail="Failed to generate title")

    def create_message(self, background_task: BackgroundTasks, user_id: str, thread_id: str, query: str):

        if not self.conversation_repository.validate_thread(user_id=user_id, thread_id=thread_id):
            raise HTTPException(
                status_code=404,
                detail=constants.CONVERSATION_NOT_FOUND
            )

        config = create_graph_config(user_id, thread_id)

        result = self.graph.invoke(
            {
                constants.MESSAGES: [
                    HumanMessage(content=query)
                ]
            },
            config=config
        )

        response = result[constants.MESSAGES][-1].content

        self.conversation_repository.update_conversation_activity(thread_id=thread_id)

        background_task.add_task(
            self.rename_conversation_if_needed,
            thread_id,
            query
        )
        return response
    
    async def stream_message(self, background_task: BackgroundTasks, user_id: str, thread_id: str, query: str):
        if not self.conversation_repository.validate_thread(user_id=user_id, thread_id=thread_id):
            raise HTTPException(
                status_code=404,
                detail=constants.CONVERSATION_NOT_FOUND
            )
    
        config = create_graph_config(user_id, thread_id)
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
        tool_citations = []

        try:
            async for event in self.graph.astream_events(
                {
                    constants.MESSAGES: [
                        HumanMessage(content=query)
                    ]
                },
                config=config,
                version=constants.V2
            ):
                event_name = event[constants.EVENT]

                if event_name == constants.ON_CHAT_MDL_STRM:
                    chunk = event[constants.DATA][constants.CHUNK]

                    if chunk.content:
                        final_response += chunk.content
                        yield sse_event(
                            constants.LLM_CHUNK,
                            {
                                constants.CONTENT: chunk.content
                            }
                        )
                elif event_name == constants.ON_TOOL_START:
                    yield sse_event(
                        constants.TOOL_CALL,
                        {
                            constants.TOOL: event[constants.NAME],
                            constants.ARGS: event[constants.DATA].get(constants.INPUT, {})
                        }
                    )
            
                elif event_name == constants.ON_TOOL_END:
                    tool_output = event[constants.DATA][constants.OUTPUT]

                    response = tool_output.content
                    citations = []

                    try:
                        payload = json.loads(tool_output.content)

                        if isinstance(payload, dict):
                            response = payload.get(constants.CNTXT, tool_output.content)
                            citations = payload.get(constants.CITATIONS, [])
                    except (json.JSONDecodeError, TypeError):
                        pass

                    if citations:
                        tool_citations.extend(citations)
                    yield sse_event(
                        constants.TOOL_RESP,
                        {
                            constants.TOOL: tool_output.name,
                            constants.TOOL_ID: tool_output.tool_call_id,
                            constants.RESPONSE: response
                        }
                    )

                    if citations:
                        yield sse_event(
                            constants.CITATIONS,
                            {
                                constants.TOOL: tool_output.name,
                                constants.CITATIONS: citations,
                            },
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

        background_task.add_task(
            self.rename_conversation_if_needed,
            thread_id,
            query,
        )
        
        yield sse_event(
            constants.CHART_MDL_END,
            {
                constants.MDL: settings.MODEL_NAME
            }
        )

        yield sse_event(
            constants.DONE,
            {
                constants.THREAD_ID: thread_id,
                constants.RESPONSE: final_response,
                constants.CITATIONS: tool_citations,
                constants.TS: str(datetime.now(timezone.utc).isoformat()),
                constants.MSG_COUNT: conversation[constants.MSG_COUNT] if conversation[constants.MSG_COUNT] else 0,
                constants.FNSH_RESON: constants.CMPLTD
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

    def get_conversation(self, thread_id: str):
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

        self.conversation_repository.delete_checkpoints(thread_id)
        self.conversation_repository.delete_checkpoint_writes(thread_id)
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

        result = self.llm.invoke(messages)
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
