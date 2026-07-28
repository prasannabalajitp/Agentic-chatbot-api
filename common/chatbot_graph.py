from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import MessagesState
from langchain_core.messages import SystemMessage
from langchain_core.messages import AIMessage, ToolMessage

from langgraph.prebuilt import ToolNode
from datetime import datetime

from llm.nvidia_llm import invoke_chat
from database.checkpointer import checkpointer
from core.constants import constants
from tools.tool_registry import registry
from common.prompt import SYSTEM_PROMPT
from pprint import pprint


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


def chatbot(state: MessagesState):

    MAX_HISTORY = 10

    current_datetime = datetime.now().strftime(constants.STRF_TIME)
    messages = [
        SystemMessage(
            content=f"""
            Today's Date and time : {current_datetime}
            The above date and time is the current system time.
            Use it whenever the user asks about:

            - today
            - yesterday
            - tomorrow
            - this week
            - this month
            - current
            - latest
            - recent

            When deciding whether information from web search is current,
            compare it against today's date.

            {SYSTEM_PROMPT}
        """),
        *state[constants.MESSAGES][-constants.MAX_HISTORY:]
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
    if (not response.content and response.additional_kwargs.get("reasoning_content")):
        response.content = response.additional_kwargs["reasoning_content"]
        return response
    print(response)
    print(response.tool_calls)
    print(response.additional_kwargs)
    print(response.response_metadata)
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
