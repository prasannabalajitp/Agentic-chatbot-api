from langchain_core.messages import AIMessage, HumanMessage
from database.checkpointer import checkpointer
from common.deepagent import deep_agent
from core.constants import constants

def get_chat_history(thread_id: str):
    config = {
        constants.CONFIGURABLE: {
            constants.THREAD_ID: thread_id
        }
    }

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
            history.append({
                constants.TYPE: constants.AI,
                constants.CONTENT: msg.content,
                constants.TOOL_CALLS: msg.tool_calls
            })

    return history
