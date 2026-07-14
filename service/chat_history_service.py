from langchain_core.messages import AIMessage, HumanMessage
from database.checkpointer import checkpointer
from core.constants import constants

def get_chat_history(thread_id: str):

    config = {
        constants.CONFIGURABLE:{
            constants.THREAD_ID: thread_id
        }
    }

    checkpoint = checkpointer.get(config)

    if checkpoint is None:
        return []
    
    messages = checkpoint[constants.CHANL_VALUES][constants.MESSAGES]
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
