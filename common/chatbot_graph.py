from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import MessagesState
from langchain_core.messages import SystemMessage
from langchain_core.messages import AIMessage, ToolMessage

from langgraph.prebuilt import ToolNode

from llm.nvidia_llm import invoke_chat
from database.checkpointer import checkpointer
from core.constants import constants
from tools.tool_registry import registry
from common.prompt import SYSTEM_PROMPT
from pprint import pprint
from copy import deepcopy


def custom_tools_condition(state: MessagesState):

    last_message = state[constants.MESSAGES][-1]

    if not isinstance(last_message, AIMessage):
        return END
    
    if not last_message.tool_calls:
        return END
    
    if len(state[constants.MESSAGES]) >=2 :
        previous_msg = state[constants.MESSAGES][-2]

        if isinstance(previous_msg, ToolMessage):
            current_tool = last_message.tool_calls[0][constants.NAME]

            if previous_msg.name == current_tool:
                print(constants.DUP_ENTRY)
        
    return constants.TOOLS


def sanitize_ai_message(message: AIMessage):
    message = deepcopy(message)
    message.additional_kwargs = {}
    message.response_metadata = {}
    message.usage_metadata = None
    return message

def chatbot(state: MessagesState):

    MAX_HISTORY = 8

    history = []
    recent_messages = state[constants.MESSAGES][-MAX_HISTORY:]
    latest_tool_index = None

    for idx in reversed(range(len(recent_messages))):
        if isinstance(recent_messages[idx], ToolMessage):
            latest_tool_index = idx
            break
    for idx, msg in enumerate(recent_messages):
        if isinstance(msg, AIMessage):
            msg = sanitize_ai_message(msg)
        else:
            msg = deepcopy(msg)

        if isinstance(msg, ToolMessage):
            if latest_tool_index is not None and idx != latest_tool_index:
                continue

        history.append(msg)

    messages = [
        SystemMessage(
            content=f"""
            {SYSTEM_PROMPT}
        """),
        *history
    ]

    print("=" * 80)
    print(f"State messages : {len(state[constants.MESSAGES])}")
    print(f"LLM messages   : {len(messages)}")

    for i, msg in enumerate(messages):
        print(i, type(msg).__name__, len(str(msg.content)))

    print("\n========== MESSAGES SENT TO LLM ==========\n")
    pprint(messages)
    print("\n==========================================\n")
    # response = chat_model.invoke(messages)
    response = invoke_chat(messages)
    # response.additional_kwargs.clear()
    # response.response_metadata = {}
    # response.usage_metadata = None
    # if (not response.content and response.additional_kwargs.get("reasoning_content")):
    #     response.content = response.additional_kwargs["reasoning_content"]
    #     return response
    if not response.content:
        response.content = "I couldn't generate final response."
    print(response)
    print(response.tool_calls)
    print(response.additional_kwargs)
    print(response.response_metadata)
    if isinstance(response, AIMessage):
        response = sanitize_ai_message(response)
    return {
        constants.MESSAGES: [response]
    }


builder = StateGraph(MessagesState)

builder.add_node(constants.CHATBOT, chatbot)
tools = registry.get_all()
builder.add_node(constants.TOOLS, ToolNode(registry.get_all()))

builder.add_edge(START, constants.CHATBOT)

builder.add_conditional_edges(constants.CHATBOT, custom_tools_condition)
builder.add_edge(constants.TOOLS, constants.CHATBOT)

graph = builder.compile(
    checkpointer=checkpointer
)
