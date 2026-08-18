from langgraph.graph import StateGraph, START, END
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.messages import AIMessage, ToolMessage

from common.state import AgentState
from llm.nvidia_llm import invoke_chat
from database.checkpointer import checkpointer
from core.constants import constants
from tools.tool_registry import registry
from common.prompt import SYSTEM_PROMPT
from common import planner
from common.executor import executor
from copy import deepcopy
from datetime import datetime, timezone
import time


def custom_tools_condition(state: AgentState):
    last_message = state[constants.MESSAGES][-1]
    if not isinstance(last_message, AIMessage):
        return END

    if not last_message.tool_calls:
        return END

    if len(state[constants.MESSAGES]) >= 2:
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

def get_conversation_history(state: AgentState):
    """
    Keep only HumanMessage and AIMessage for conversation history.

    ToolMessages are intentionally excluded here because current tool
    results are added separately in chatbot().
    """
    messages = state[constants.MESSAGES]
    history = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            if msg.content:
                history.append(HumanMessage(content=msg.content))

        elif isinstance(msg, AIMessage):
            if msg.content:
                history.append(AIMessage(content=msg.content))

    return history

def get_planner_context(state: AgentState):
    return get_conversation_history(state)

def planner_node(state: AgentState):
    print("=" * 50)
    print("PLANNER NODE EXECUTED")
    print("Incoming state:", state)
    current_step = state.get(constants.CURR_STEP, 0)

    if current_step >= 3:
        return {
            constants.PLAN: {
                constants.NEED_TOOLS: False,
                constants.TOOLS: [],
                constants.REASON: constants.MAX_ITR
            },
            constants.CURR_STEP: current_step
        }
    current_step += 1

    history = get_planner_context(state)

    plan = planner.plan(history)

    executed_tools = state.get(constants.TOOL_RES,[])

    if plan.get(constants.NEED_TOOLS, False):
        filtered_tools = []

        for planned_tool in plan.get(constants.TOOLS,[]):
            tool_name = planned_tool.get(constants.TOOL)

            tool_args = planned_tool.get(constants.ARGS1,{})

            normalized_args = normalize_tool_args(tool_name,tool_args)
            already_executed = any(
                result.get(constants.TOOL) == tool_name
                and normalize_tool_args(
                    result.get(constants.TOOL),
                    result.get(
                        constants.ARGS1,
                        {}
                    )
                ) == normalized_args
                and result.get(
                    constants.FILE_STATUS
                ) == constants.SUCC
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
            plan[constants.REASON] = constants.PLANNER_REASON

    result = {
        constants.PLAN: plan,
        constants.CURR_STEP: current_step
    }

    print(f"Planner Returning : {result}")
    return result

def planner_condition(state: AgentState):
    plan = state.get(constants.PLAN)

    if not plan:
        return constants.CHATBOT

    if plan.get(constants.NEED_TOOLS, False):
        return constants.EXECUTOR

    return constants.CHATBOT

def chatbot(state: AgentState):

    print("=" * 50)
    print("CHATBOT STATE KEYS:", state.keys())
    print("CHATBOT STATE:", state)
    current_datetime = (datetime.now(timezone.utc).isoformat())
    history = get_conversation_history(state)

    print("\n========== CONVERSATION HISTORY ==========\n")

    for i, msg in enumerate(history):
        print(i,    type(msg).__name__, repr(msg.content))

    print("\n==========================================\n")

    tool_context = []
    message_state = state[constants.MESSAGES]
    latest_human_index = None

    for idx in range(len(message_state) - 1,    -1, -1):

        if isinstance(message_state[idx],HumanMessage):
            latest_human_index = idx
            break

    if latest_human_index is not None:
        for msg in message_state[latest_human_index + 1:]:
            if isinstance(msg,  ToolMessage):
                tool_context.append(deepcopy(msg))

    citations = state.get(constants.CITATIONS, [])

    messages = [
        SystemMessage(
            content=f"""
Current datetime:
{current_datetime}

{SYSTEM_PROMPT}
"""
        ),
        *history[-10:],
        *tool_context,
    ]
    if citations:
        citation_context = "\n".join(
            f"- {citation.get(constants.TITLE, '')}: "
            f"{citation.get(constants.URL, '')}"
            for citation in citations
        )
        messages.append(
            SystemMessage(
                content=(
                    "Sources for the tool information above:\n"
                    f"{citation_context}"
                )
            )
        )
    print("\n========== MESSAGES SENT TO LLM ==========\n")
    for i, msg in enumerate(messages):
        print(i,type(msg).__name__,repr(msg.content))

    print("\n==========================================\n")
    start_time = time.time()
    response = invoke_chat(messages)
    print(
        f"CHATBOT LLM TIME : "
        f"{time.time() - start_time:.2f} seconds"
    )

    if not response.content:
        response.content = (constants.ERR_GEN_RES)

    finish_reason = (response.response_metadata.get(constants.FNSH_RESON))

    if (finish_reason == constants.LEN  and not response.tool_calls):
        raise RuntimeError(constants.EXH_REQ)

    return {
        constants.MESSAGES: [
            sanitize_ai_message(response)
        ]
    }


def executor_condition(state: AgentState):
    plan = state.get(constants.PLAN)

    if (not plan or not plan.get(constants.NEED_TOOLS, False)):
        return constants.CHATBOT

    return constants.PLANNER


# ============================================================
# GRAPH
# ============================================================

builder = StateGraph(AgentState)
builder.add_node(constants.PLANNER,planner_node)
builder.add_node(constants.CHATBOT,chatbot)
builder.add_node(constants.EXECUTOR,executor)

tools = registry.get_all()

builder.add_edge(START,constants.PLANNER)

builder.add_conditional_edges(constants.PLANNER,planner_condition,
    {
        constants.EXECUTOR: constants.EXECUTOR,
        constants.CHATBOT: constants.CHATBOT,
    },
)

# builder.add_edge(constants.EXECUTOR,executor_condition)
builder.add_conditional_edges(
    constants.EXECUTOR, 
    executor_condition,
    {
        constants.PLANNER: constants.PLANNER,
        constants.CHATBOT: constants.CHATBOT
    },
)

graph = builder.compile(checkpointer=checkpointer)
