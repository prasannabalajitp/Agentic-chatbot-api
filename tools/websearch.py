from langchain.tools import tool
from tools.decorator import register_tool
from core.constants import constants
from common.tool_result import ToolResult


from service.web_search_service import WebSearchService
import logging

from tools.tool_registry import ToolRisk

logger = logging.getLogger(__name__)

web_search_service = WebSearchService()


def web_search_impl(query: str, context=None) -> ToolResult:
    result = web_search_service.search(query)
    return result

@register_tool(name=constants.WEB_SRCH, handler=web_search_impl, category=constants.GEN, risk=ToolRisk.LOW)
@tool
def web_search(query: str) -> ToolResult:
    """
    Search the internet for recent information.

    Args:
        query: The complete search query representing the user's intent.

    Returns:
        Structured search result containing summary, citations,
        and execution metadata.
    """
    result = web_search_impl(query=query)

    logger.info("LANGCHAIN TOOL RETURN: %r", result)

    return result
