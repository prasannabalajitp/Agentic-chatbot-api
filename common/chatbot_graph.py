from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import MessagesState
from langchain_core.messages import SystemMessage
from langchain_core.messages import AIMessage, ToolMessage

from langgraph.prebuilt import ToolNode
from datetime import datetime

from llm.nvidia_llm import chat_model
from tools import TOOLS
from database.checkpointer import checkpointer
from core.constants import constants
from common.prompt import SYSTEM_PROMPT


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
                print("Duplicate tool detected. Ending graph.")
                return END
        
    return constants.TOOLS


def chatbot(state: MessagesState):

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
        *state[constants.MESSAGES]
    ]

    response = chat_model.invoke(messages)
    return {
        constants.MESSAGES: [response]
    }


builder = StateGraph(MessagesState)

builder.add_node(constants.CHATBOT, chatbot)
builder.add_node(constants.TOOLS, ToolNode(TOOLS))

builder.add_edge(START, constants.CHATBOT)

builder.add_conditional_edges(constants.CHATBOT, custom_tools_condition)
builder.add_edge(constants.TOOLS, constants.CHATBOT)

graph = builder.compile(
    checkpointer=checkpointer
)
