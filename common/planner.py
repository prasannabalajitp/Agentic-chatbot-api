from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage

from common.prompt import PLANNER_PROMPT
from llm.nvidia_llm import llm
import json

def plan(messages: list[BaseMessage]):
    planner_messages = [
        SystemMessage(content=PLANNER_PROMPT),
        *messages[-6:]
    ]
    response = llm.invoke(planner_messages)
    try:
        return json.loads(response.content)
    except Exception:
        return {
            "needs_tools": False,
            "tools": [],
            "steps": [],
            "reason": "Planner could not generate a valid plan."
        }
