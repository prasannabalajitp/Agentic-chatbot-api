from datetime import datetime, timezone
import logging

from fastapi import BackgroundTasks, HTTPException

from common.sse import sse_event
from core.config import settings
from core.constants import constants
from context.agent_context import AgentContext
from context.agent_event import AgentEventType
from repository.conversation_repository import ConversationRepository
from repository.file_repository import FileRepository
from service.agent_service import AgentService
from service.guardrail_service import GuardRailService
from service.title_service import TitleService


logger = logging.getLogger(__name__)


class ChatService:

    def __init__(self, agent_service: AgentService, conversation_repository: ConversationRepository, guardrail_service: GuardRailService, title_service: TitleService, file_repository: FileRepository):
        self.agent_service = agent_service
        self.conversation_repository = conversation_repository
        self.file_repository = file_repository
        self.guardrails = guardrail_service
        self.title_service = title_service

    def _create_agent_context(self, user_id: str, thread_id: str, query: str) -> AgentContext:
        uploaded_files = self.file_repository.get_thread_files(user_id=user_id, thread_id=thread_id)

        return AgentContext(
            user_id=user_id,
            thread_id=thread_id,
            query=query,
            uploaded_files=uploaded_files,
        )

    def create_message(self, background_task: BackgroundTasks, user_id: str, thread_id: str, query: str):
        if not self.conversation_repository.validate_thread(user_id=user_id, thread_id=thread_id):
            raise HTTPException(
                status_code=404,
                detail=constants.CONVERSATION_NOT_FOUND,
            )

        self.guardrails.validate_prompt(query)
        context = self._create_agent_context(user_id=user_id, thread_id=thread_id, query=query)
        result = self.agent_service.invoke(context)

        logger.info("Agent execution completed | user=%s | thread=%s", user_id, thread_id)
        # response = result[constants.MESSAGES][-1].content
        response = result.response
        response = self.guardrails.validate_response(response)
        self.conversation_repository.update_conversation_activity(thread_id=thread_id)

        background_task.add_task(
            self.title_service.rename_conversation_if_needed,
            user_id,
            thread_id,
            query,
        )

        return {
            constants.RESPONSE: response,
            constants.CITATIONS: result.citations
        }

    async def stream_message(self, background_task: BackgroundTasks, user_id: str, thread_id: str,query: str):

        if not self.conversation_repository.validate_thread(user_id=user_id, thread_id=thread_id):
            raise HTTPException(
                status_code=404,
                detail=constants.CONVERSATION_NOT_FOUND,
            )
        try:
            self.guardrails.validate_prompt(query)

        except HTTPException as e:
            yield sse_event(
                constants.ERR,
                {
                    constants.MSG: e.detail,
                },
            )
            return

        yield sse_event(
            constants.CHART_STRT,
            {
                constants.USER_ID: user_id,
                constants.THREAD_ID: thread_id,
                constants.QUERY: query,
            },
        )

        final_response = constants.EMPTY_STRING
        final_citations = []
        tool_call_count = 0

        try:
            context = self._create_agent_context(user_id=user_id, thread_id=thread_id, query=query)

            async for event in self.agent_service.stream(context):
                logger.debug("AGENT EVENT | type=%s | tool=%s", event.type, event.tool_name)

                if event.type == AgentEventType.MODEL_START:
                    yield sse_event(
                        constants.CHART_MDL_STRT,
                        {
                            constants.MDL: settings.MODEL_NAME,
                        },
                    )
                elif event.type == AgentEventType.LLM_CHUNK:
                    if event.content:
                        final_response += event.content
                        yield sse_event(
                            constants.LLM_CHUNK,
                            {
                                constants.CONTENT: event.content,
                            },
                        )
                elif event.type == AgentEventType.MODEL_END:
                    logger.debug("MODEL END | has_tool_call=%s", event.has_tool_call)

                    yield sse_event(
                        constants.ON_CHAT_MDL_END,
                        {
                            constants.MDL: settings.MODEL_NAME,
                        },
                    )
                elif event.type == AgentEventType.TOOL_START:
                    tool_call_count += 1
                    tool_name = event.tool_name
                    self.guardrails.validate_tool(tool_name=tool_name, tool_calls=tool_call_count)

                    yield sse_event(
                        constants.TOOL_CALL,
                        {
                            constants.TOOL: tool_name,
                            constants.ARGS: event.arguments or {},
                        },
                    )
                elif event.type == AgentEventType.TOOL_END:
                    logger.debug("TOOL END | tool=%s | tool_id=%s", event.tool_name, event.tool_id)

                    if event.citations:
                        final_citations.extend(event.citations)
                        logger.debug("CITATIONS FOUND: %s", event.citations)

                    yield sse_event(
                        constants.TOOL_RESP,
                        {
                            constants.TOOL: event.tool_name,
                            constants.TOOL_ID: event.tool_id,
                            constants.RESPONSE: event.result,
                        },
                    )

        except Exception as e:
            logger.exception("Agent streaming failed | user=%s | thread=%s", user_id, thread_id)

            yield sse_event(
                constants.ERR,
                {
                    constants.TYPE: type(e).__name__,
                    constants.MSG: str(e),
                },
            )
            return

        if final_citations:
            self.agent_service.persist_citations(context=context, citations=final_citations)
            
        self.conversation_repository.update_conversation_activity(thread_id=thread_id,)
        yield sse_event(
            constants.CONV_ACTY,
            {
                constants.THREAD_ID: thread_id,
            },
        )

        conversation = self.conversation_repository.get_thread(thread_id=thread_id,)
        logger.debug("CONVERSATION: %s", conversation)
        
        background_task.add_task(
            self.title_service.rename_conversation_if_needed,
            user_id,
            thread_id,
            query,
        )
        try:
            final_response = self.guardrails.validate_response(final_response)

        except Exception as e:
            yield sse_event(
                constants.ERR,
                {
                    constants.MSG: str(e),
                },
            )
            return
        yield sse_event(
            constants.CHART_MDL_END,
            {
                constants.MDL: settings.MODEL_NAME,
            },
        )
        yield sse_event(
            constants.DONE,
            {
                constants.THREAD_ID: thread_id,
                constants.RESPONSE: final_response,
                constants.CITATIONS: final_citations,
                constants.TS: datetime.now(
                    timezone.utc
                ).isoformat(),
                constants.MSG_COUNT: (
                    conversation[constants.MSG_COUNT]
                    if conversation[constants.MSG_COUNT]
                    else 0
                ),
                constants.FNSH_RESON: constants.CMPLTD,
            },
        )
