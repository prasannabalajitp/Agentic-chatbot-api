from langchain_nvidia_ai_endpoints import ChatNVIDIA

from core.config import settings
from tools import TOOLS

llm = ChatNVIDIA(
    api_key=settings.NVIDIA_API_KEY,
    model=settings.MODEL_NAME,
    temperature=0
)

chat_model = llm.bind_tools(TOOLS)
