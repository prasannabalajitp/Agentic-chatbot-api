from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.messages import AIMessage, HumanMessage

from core.config import settings
from core.constants import constants
from tools.tool_registry import registry

import json

llm = ChatNVIDIA(
    api_key=settings.NVIDIA_API_KEY,
    model=settings.MODEL_NAME,
    temperature=0
)

title_llm = ChatNVIDIA(
    api_key=settings.NVIDIA_API_KEY,
    model=constants.TITLE_MDL,
    temperature=0,
)

rag_llm = ChatNVIDIA(
    model=constants.RAG_MDL
)

chat_model = llm.bind_tools(registry.get_all())

def invoke_chat(messages):
    """
    Wrapper around ChatNVIDIA to normalize responses.
    Some Nemotron responses return the final answer in
    additional_kwargs['reasoning_content'] with an empty content.
    """

    response = chat_model.invoke(messages)

    if (not response.content and response.additional_kwargs.get(constants.RSNG_CNTNT)):
        response.content = response.additional_kwargs[constants.RSNG_CNTNT].replace(
            constants.THINK, constants.EMPTY_STRING
        ).strip()

    if isinstance(response, AIMessage) and response.tool_calls:

        current = response.tool_calls[0]

        current_key = (
            current[constants.NAME],
            json.dumps(current.get("args", {}), sort_keys=True),
        )

        previous_key = None

        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                break

            if isinstance(msg, AIMessage) and msg.tool_calls:
                prev = msg.tool_calls[0]

                previous_key = (
                    prev["name"],
                    json.dumps(prev.get("args", {}), sort_keys=True),
                )
                break

        if previous_key is not None and current_key == previous_key:
            response.tool_calls = []

            response.content = (
                "The requested tool has already been executed. "
                "Use the previous tool result to answer the user."
            )

    return response
