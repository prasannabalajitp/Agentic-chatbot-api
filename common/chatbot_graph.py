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
import json, time


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
                raise(constants.DUP_ENTRY)
        
    return constants.TOOLS


def sanitize_ai_message(message: AIMessage):
    message = deepcopy(message)
    message.additional_kwargs = {}
    message.response_metadata = {}
    message.usage_metadata = None

    if message.tool_calls:
        message.content = ""

    return message

def normalize_tool_args(tool_name: str, args: dict) -> dict:
    normalized = deepcopy(args)
    if tool_name == constants.CALCULATOR:
        expr = normalized.get(constants.EXPR)
        if expr:
            normalized[constants.EXPR] = (
                expr.replace(" ", "")
                    .replace("×", "*")
            )
    return normalized


def get_planner_context(state: AgentState):
    messages = state[constants.MESSAGES]
    latest_human_index = None

    for idx in range(len(messages) - 1, -1, -1):
        if isinstance(messages[idx], HumanMessage):
            latest_human_index = idx
            break

    if latest_human_index is None:
        return []

    context = []
    previous_messages = messages[
        max(0, latest_human_index - 2):latest_human_index
    ]
    for msg in previous_messages:
        if isinstance(msg, ToolMessage):
            continue
        if isinstance(msg, AIMessage):
            context.append(sanitize_ai_message(msg))
        else:
            context.append(deepcopy(msg))
    context.append(
        deepcopy(messages[latest_human_index])
    )
    for msg in messages[latest_human_index + 1:]:
        if isinstance(msg, ToolMessage):
            context.append(deepcopy(msg))
    return context

def planner_node(state: AgentState):

    history = get_planner_context(state)

    plan = planner.plan(history)
    executed_tools = state.get(constants.TOOL_RES, [])
    if plan.get(constants.NEED_TOOLS, False):
        filtered_tools = []
        for planned_tool in plan.get(constants.TOOLS, []):
            tool_name = planned_tool.get(constants.TOOL)
            tool_args = planned_tool.get(constants.ARGS1, {})
            normalized_args = normalize_tool_args(
                tool_name,
                tool_args
            )
            already_executed = any(
                result.get(constants.TOOL) == tool_name
                and normalize_tool_args(
                    result.get(constants.TOOL),
                    result.get(constants.ARGS1, {})
                ) == normalized_args
                and result.get(constants.FILE_STATUS) == constants.SUCC
                for result in executed_tools
            )
            if already_executed:
                print(
                    f"Skipping duplicate tool call: "
                    f"{tool_name} {tool_args}"
                )
                continue

            filtered_tools.append(planned_tool)
        plan[constants.TOOLS] = filtered_tools

        if not filtered_tools:
            plan[constants.NEED_TOOLS] = False
            plan[constants.REASON] = (
                "All requested tool calls have already been executed "
                "successfully. Use the existing tool results."
            )

    result = {
        constants.PLAN: plan
    }
    return result

def planner_condition(state: AgentState):
    plan = state.get(constants.PLAN)

    if not plan:
        return constants.CHATBOT

    if plan.get(constants.NEED_TOOLS, False):
        return constants.EXECUTOR

    return constants.CHATBOT

def chatbot(state: AgentState):
    current_datetime = datetime.now(timezone.utc).isoformat()
    messages_state = state[constants.MESSAGES]
    latest_human_index = None

    for idx in range(len(messages_state) - 1, -1, -1):
        if isinstance(messages_state[idx], HumanMessage):
            latest_human_index = idx
            break

    if latest_human_index is None:
        history = []
    else:
        history = []

        previous_messages = messages_state[
            max(0, latest_human_index - 2):latest_human_index
        ]

        for msg in previous_messages:
            if isinstance(msg, ToolMessage):
                continue
            if isinstance(msg, AIMessage):
                history.append(
                    sanitize_ai_message(msg)
                )
            else:
                history.append(
                    deepcopy(msg)
                )
        history.append(
            deepcopy(messages_state[latest_human_index])
        )

        for msg in messages_state[latest_human_index + 1:]:
            if isinstance(msg, ToolMessage):
                history.append(
                    deepcopy(msg)
                )

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
    print("\n========== MESSAGES SENT TO LLM ==========\n")
    for i, msg in enumerate(messages):
        print(
            i,
            type(msg).__name__,
            repr(msg.content)
        )
    print("\n==========================================\n")
    start_time = time.time()
    response = invoke_chat(messages)
    print(
        f"CHATBOT LLM TIME : "
        f"{time.time() - start_time:.2f} seconds"
    )
    if not response.content:
        response.content = (
            constants.ERR_GEN_RES
        )

    finish_reason = response.response_metadata.get(
        constants.FNSH_RESON
    )

    if (
        finish_reason == constants.LEN
        and not response.tool_calls
    ):
        raise RuntimeError(
            constants.EXH_REQ
        )

    return {
        constants.MESSAGES: [
            sanitize_ai_message(response)
        ]
    }

def executor_condition(state: AgentState):
    plan = state.get(constants.PLAN)

    if not plan or not plan.get(constants.NEED_TOOLS, False):
        return constants.CHATBOT

    return constants.PLANNER

builder = StateGraph(AgentState)

builder.add_node(constants.PLANNER, planner_node)
builder.add_node(constants.CHATBOT, chatbot)
builder.add_node(constants.EXECUTOR, executor)
tools = registry.get_all()

builder.add_edge(START, constants.PLANNER)
builder.add_conditional_edges(
    constants.PLANNER,
    planner_condition,
    {
        constants.EXECUTOR: constants.EXECUTOR,
        constants.CHATBOT: constants.CHATBOT,
    },
)

builder.add_edge(constants.EXECUTOR, constants.PLANNER)

graph = builder.compile(
    checkpointer=checkpointer
)
