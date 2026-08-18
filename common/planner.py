from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage

from common.prompt import PLANNER_PROMPT
from core.constants import constants
from llm.nvidia_llm import llm
import json
import time

def plan(messages: list[BaseMessage]):
    planner_messages = [
        SystemMessage(content=PLANNER_PROMPT),
        *messages[-10:]
    ]

    response = llm.invoke(planner_messages)
    content = response.content.strip()

    print("========== PLANNER RAW RESPONSE ==========")
    print("CONTENT:", repr(content))
    print("REASONING:", repr(
        response.additional_kwargs.get(constants.RSNG_CNTNT)
    ))
    print("==========================================")

    if not content:
        raise RuntimeError(constants.EMPTY_CNTNT)

    try:
        return json.loads(content)
    except json.JSONDecodeError as ex:
        return {
            constants.NEED_TOOLS: False,
            constants.TOOLS: [],
            constants.REASON: constants.NON_JSON_RESP
        }
