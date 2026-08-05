from langchain_nvidia_ai_endpoints import ChatNVIDIA

from core.config import settings
from service.guardrail_service import GuardRailService

guardrail_llm = ChatNVIDIA(
    api_key=settings.NVIDIA_API_KEY,
    model=settings.MODEL_NAME,
    temperature=0,
)

guardrail_service = GuardRailService(guardrail_llm)
