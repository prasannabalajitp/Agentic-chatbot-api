import json
import logging

from langchain_core.messages import HumanMessage

from common.configurable import create_graph_config
from context.agent_context import AgentContext
from context.agent_event import AgentEvent, AgentEventType
from core.constants import constants
from context.agent_event import AgentEvent


logger = logging.getLogger(__name__)


class AgentService:

    def __init__(self, deepagent):
        self.deepagent = deepagent

    def create_config(self, context: AgentContext):
        config = create_graph_config(user_id=context.user_id, thread_id=context.thread_id)

        config[constants.CONFIGURABLE][constants.UPLDED_FIELS] = (
            context.uploaded_files
        )
        return config

    def _create_input(self, context: AgentContext):
        return {
            constants.MESSAGES: [
                HumanMessage(content=context.query)
            ]
        }

    def _extract_chunk_content(self, chunk) -> str:
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


    def _normalize_event(self, event) -> AgentEvent | None:

        event_name = event.get(constants.EVENT)
        data = event.get(constants.DATA, {})
        name = event.get(constants.NAME)

        logger.debug("RAW AGENT EVENT | event=%s | name=%s", event_name, name)

        if event_name == constants.ON_CHAT_MDL_STRT:
            return AgentEvent(
                type=constants.MDL_STRT
            )

        if event_name == constants.ON_CHAT_MDL_STRM:
            chunk = data.get(constants.CHUNK)
            content = self._extract_chunk_content(chunk)

            if content:
                return AgentEvent(
                    type=constants.LLM_CHUNK,
                    content=content
                )
            return None

        if event_name == constants.ON_CHAT_MDL_END:
            output = data.get(constants.OUTPUT)
            logger.debug("MODEL END OUTPUT: %r", output)
            tool_calls = getattr(output, constants.TOOL_CALLS, []) or []

            return AgentEvent(
                type=constants.MDL_END,
                has_tool_call=bool(tool_calls),
                content=None
            )

        if event_name == constants.ON_TOOL_START:
            return AgentEvent(type=constants.TOOL_STRT, tool_name=name, arguments=data.get(constants.INPUT, {}))

        if event_name == constants.ON_TOOL_END:
            tool_output = data.get(constants.OUTPUT)
            if not tool_output:
                return AgentEvent(type=constants.TOOL_END, tool_name=name)

            tool_name = getattr(tool_output, constants.NAME, name)
            tool_id = getattr(tool_output, constants.TOOL_ID, constants.EMPTY_STRING)
            tool_content = getattr(tool_output, constants.CONTENT, constants.EMPTY_STRING)

            citations = []

            if isinstance(tool_content, str):
                try:
                    tool_result = json.loads(tool_content)
                    citations = tool_result.get(constants.CITATIONS, [])
                    if not isinstance(citations, list):
                        citations = []

                except (json.JSONDecodeError, TypeError):
                    logger.debug("Tool output is not JSON: %r", tool_content)

            return AgentEvent(
                type=constants.TOOL_END,
                tool_name=tool_name,
                tool_id=tool_id,
                result=tool_content,
                citations=citations
            )

        return None


    def invoke(self, context: AgentContext):
        """
        Execute the DeepAgent synchronously.
        """
        config = self.create_config(context)
        input_data = self._create_input(context)
        logger.info("Invoking DeepAgent | user=%s | thread=%s", context.user_id, context.thread_id)

        result = self.deepagent.invoke(
            input_data,
            config=config
        )
        return result

    async def stream(self, context: AgentContext):
        """
        Stream raw DeepAgent/LangGraph events.
        AgentService owns the DeepAgent-specific event source.
        ChatService can consume these events without knowing
        how the DeepAgent is invoked.
        """
        config = self.create_config(context)
        input_data = self._create_input(context)
        logger.info(
            "Streaming DeepAgent | user=%s | thread=%s",
            context.user_id,
            context.thread_id,
        )

        async for event in self.deepagent.astream_events(
            input_data,
            config=config,
            version=constants.V2,
        ):
            agent_event = self._normalize_event(event)
            if agent_event:
                yield agent_event

    
