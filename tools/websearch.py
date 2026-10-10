import logging

from langchain.tools import tool

from common.tool_result import ToolResult
from core.constants import constants
from service.web_search_service import WebSearchService
from tools.decorator import register_tool
from tools.tool_registry import ToolRisk

logger = logging.getLogger(__name__)

web_search_service = WebSearchService()


def web_search_impl(query: str, context=None) -> ToolResult:
    if not query or not query.strip():
        return {
            constants.SUMMARY: "Please provide a search query.",
            constants.CITATIONS: [],
            constants.METADATA: {
                constants.SUCC: False,
                constants.RETRYABLE: False,
            },
        }

    result = web_search_service.search(query)
    return result


@register_tool(name=constants.WEB_SRCH, handler=web_search_impl, category=constants.GEN, risk=ToolRisk.LOW)
@tool
def web_search(query: str) -> ToolResult:
    """Search the internet for information relevant to the user's query.

    Args:
        query: The complete search query representing the user's intent.

    Returns:
        Structured search results containing a summary, citations,
        and execution metadata.
    """
    result = web_search_impl(query=query)
    logger.info("Web search tool completed.")
    return result
