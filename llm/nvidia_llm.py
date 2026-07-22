from langchain_nvidia_ai_endpoints import ChatNVIDIA

from core.config import settings
from core.constants import constants
# from tools import TOOLS
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
