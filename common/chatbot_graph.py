from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import MessagesState
from langchain_core.messages import SystemMessage
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.runnables import RunnableConfig

from langgraph.prebuilt import ToolNode
from datetime import datetime

from llm.nvidia_llm import chat_model
from tools import TOOLS
from database.checkpointer import checkpointer
from core.constants import constants
from common.prompt import SYSTEM_PROMPT



def custom_tools_condition(state: MessagesState):
    last_message = state[constants.MESSAGES][-1]

    if (
        isinstance(last_message, AIMessage)
        and last_message.tool_calls
    ):
        return constants.TOOLS

    return END
# ----------------------------
# Chatbot Node
# ----------------------------

def chatbot(state: MessagesState, config: RunnableConfig):

    print("\n========== CHATBOT NODE ==========")
    print(state)

    # response = llm.invoke(state[constants.MESSAGES])
    current_datetime = datetime.now().strftime(constants.STRF_TIME)
    user_id = config[constants.CONFIGURABLE][constants.USER_ID]
    thread_id = config[constants.CONFIGURABLE][constants.THREAD_ID]
    messages = [
        SystemMessage(
            content=f"""
            Current Runtime Context

            user_id = "{user_id}"

            thread_id = "{thread_id}"
            
            These values MUST be used whenever a tool requires them.
            Do not change them.
            Do not invent new values.

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


# ----------------------------
# Build Graph
# ----------------------------
builder = StateGraph(MessagesState)

builder.add_node(constants.CHATBOT, chatbot)
builder.add_node(constants.TOOLS, ToolNode(TOOLS))

builder.add_edge(START, constants.CHATBOT)

builder.add_conditional_edges(constants.CHATBOT, custom_tools_condition)
builder.add_edge(constants.TOOLS, constants.CHATBOT)

graph = builder.compile(
    checkpointer=checkpointer
)
