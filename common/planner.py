# from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage

# from common.prompt import PLANNER_PROMPT
# from core.constants import constants
# from llm.nvidia_llm import planner_llm, llm
# from models.tool_model import ToolCall, Plan
# import json
# import time


# # def plan(messages: list[BaseMessage]):
# #     planner_messages = [
# #         SystemMessage(content=PLANNER_PROMPT),
# #         *messages[-10:]
# #     ]

# #     response = planner_llm.invoke(planner_messages)
# #     content = response.content.strip()
# #     print(f'{content}')

# #     print("========== PLANNER RAW RESPONSE ==========")
# #     print("CONTENT:", repr(content))
# #     print("REASONING:", repr(
# #         response.additional_kwargs.get(constants.RSNG_CNTNT)
# #     ))
# #     print("==========================================")

# #     if not content:
# #         raise RuntimeError(constants.EMPTY_CNTNT)

# #     try:
# #         return json.loads(content)
# #     except json.JSONDecodeError as ex:
# #         start = content.find("{")
# #         end = content.find("}")
# #         if start != -1 and end != -1 and end > start:
# #             json_content = content[start:end + 1]
# #             try:
# #                 return json.loads(json_content)
# #             except json.JSONDecodeError:
# #                 pass
            
# #         raise RuntimeError(
# #         f"Planner returned invalid JSON: {ex}. "
# #         f"Raw content: {content}"
# #     )

# def plan(messages: list[BaseMessage]):

#     planner_messages = [
#         SystemMessage(content=PLANNER_PROMPT),
#         *messages[-10:]
#     ]

#     response = planner_llm.invoke(planner_messages)
#     content = response.content.strip()

#     print("========== PLANNER RESPONSE ==========")
#     print("PLAN:", response)
#     print("======================================")

#     if not response:
#         raise RuntimeError(constants.EMPTY_CNTNT)

#     return response.model_dump()


from langchain_core.messages import BaseMessage, SystemMessage

from common.prompt import PLANNER_PROMPT
from llm.nvidia_llm import planner_llm
from models.tool_model import Plan


def plan(messages: list[BaseMessage]):

    planner_messages = [
        SystemMessage(content=PLANNER_PROMPT),
        *messages[-10:]
    ]

    response = planner_llm.invoke(planner_messages)
    content = response.content.strip()
    try:
        return Plan.model_validate_json(content).model_dump()
    except Exception as ex:
        raise RuntimeError(
            f"Planner returned invalid plan: {ex}. Raw content: {content}"
        )
