from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage

from common.prompt import PLANNER_PROMPT
from llm.nvidia_llm import llm
import json
import time

def plan(messages: list[BaseMessage]):
    planner_messages = [
        SystemMessage(content=PLANNER_PROMPT),
        *messages[-10:]
    ]
    start_time = time.time()
    response = llm.invoke(planner_messages)

    try:
        return json.loads(response.content)
    except Exception as ex:
        raise RuntimeError(
            f"Planner failed to generate a valid plan: {ex}"
        )
