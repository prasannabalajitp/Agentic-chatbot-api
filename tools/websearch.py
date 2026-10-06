from langchain.tools import tool
from tools.decorator import register_tool
from core.constants import constants
from common.tool_result import ToolResult

from typing import Any

from service.web_search_service import WebSearchService
import logging

logger = logging.getLogger(__name__)

web_search_service = WebSearchService()

def web_search_impl(query: str, context=None) -> ToolResult:
    result = web_search_service.search(query)
    return result

@register_tool(name=constants.WEB_SRCH, handler=web_search_impl, category=constants.GEN)
@tool
def web_search(query: str) -> dict[str, Any]:
    """
    Search the internet for recent information.

    Args:
        query: The complete search query representing the user's intent.

    Returns:
        Search results as plain text.
    """
    return web_search_impl(query=query)
