from langchain.tools import tool

from typing import Any

from service.web_search_service import WebSearchService

web_search_service = WebSearchService()


@tool
def web_search(query: str) -> dict[str, Any]:
    """
    Search the internet for recent information.

    Args:
        query: The complete search query representing the user's intent.

    Returns:
        Search results as plain text.
    """
    return web_search_service.search(query)
