from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import MessagesState
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.messages import AIMessage, ToolMessage

from langgraph.prebuilt import ToolNode

from common.state import AgentState
from llm.nvidia_llm import invoke_chat
from database.checkpointer import checkpointer
from core.constants import constants
from tools.tool_registry import registry
from common.prompt import SYSTEM_PROMPT
from common import planner
from common.executor import executor
from pprint import pprint
from copy import deepcopy
from datetime import datetime, timezone
import json


def custom_tools_condition(state: AgentState):

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

    if message.tool_calls:
        message.content = ""

    return message


def planner_node(state: AgentState):

    history = state[constants.MESSAGES][-6:]

    plan = planner.plan(history)
    result = {
        "plan": plan
    }

    return result

def chatbot(state: AgentState):
    MAX_HISTORY = 8

    history = []
    recent_messages = state[constants.MESSAGES][-MAX_HISTORY:]
    latest_tool_index = None
    current_datetime = datetime.now(timezone.utc).isoformat()

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
            Current datetime:
            {current_datetime}

            {SYSTEM_PROMPT}
            """
        ),
        *history,
    ]

    for i, msg in enumerate(messages):
        print(i, type(msg).__name__, len(str(msg.content)))

    response = invoke_chat(messages)
    if not response.content:
        response.content = "I couldn't generate final response."

    finish_reason = response.response_metadata.get("finish_reason")
    if finish_reason == "length" and not response.tool_calls:
        raise RuntimeError(
            "Model exhausted completion tokens before producing a final answer."
        )

    return {
        constants.MESSAGES: [sanitize_ai_message(response)]
    }


builder = StateGraph(AgentState)

builder.add_node(constants.PLANNER, planner_node)
builder.add_node(constants.CHATBOT, chatbot)
builder.add_node(constants.EXECUTOR, executor)
tools = registry.get_all()

builder.add_edge(START, constants.PLANNER)
builder.add_edge(constants.PLANNER, constants.EXECUTOR)
builder.add_edge(constants.EXECUTOR, constants.CHATBOT)

graph = builder.compile(
    checkpointer=checkpointer
)
