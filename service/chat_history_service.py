from langchain_core.messages import AIMessage, HumanMessage
from common.deepagent import deep_agent
from core.constants import constants
from exceptions.agent import AgentConfigurationError, AgentExecutionError, AgentTimeoutError

import logging

logger = logging.getLogger(__name__)

def get_chat_history(thread_id: str):
    config = {
        constants.CONFIGURABLE: {
            constants.THREAD_ID: thread_id
        }
    }
    try:
        state = deep_agent.get_state(config)
        if not state or not state.values:
            return []

        messages = state.values.get(constants.MESSAGES, [])
        history = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                history.append({
                    constants.TYPE: constants.HUMAN,
                    constants.CONTENT: msg.content
                })

            elif isinstance(msg, AIMessage):
                metadata = msg.response_metadata or {}
                history.append({
                    constants.TYPE: constants.AI,
                    constants.CONTENT: msg.content,
                    constants.TOOL_CALLS: msg.tool_calls,
                    constants.CITATIONS: metadata.get(
                        constants.CITATIONS,
                        []
                    ),
                    constants.ARTIFACT_DATA: metadata.get(
                        constants.ARTIFACTS,
                        []
                    )
                })

        return history

    except (AgentConfigurationError, AgentExecutionError, AgentTimeoutError):
        raise

    except Exception as e:
        logger.exception("Failed to retrieve chat history | thread=%s", thread_id)
        raise AgentExecutionError from e
