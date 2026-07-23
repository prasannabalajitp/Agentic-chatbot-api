from langchain_nvidia_ai_endpoints import ChatNVIDIA

from core.config import settings
from core.constants import constants
from tools.tool_registry import registry

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

    return response
