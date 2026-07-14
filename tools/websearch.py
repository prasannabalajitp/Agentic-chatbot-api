from langchain.tools import tool

from service.web_search_service import WebSearchService

web_search_service = WebSearchService()


@tool
def web_search(query: str) -> str:
    """
    Search the internet for recent information.

    Args:
        query: The complete search query representing the user's intent.

    Returns:
        Search results as plain text.
    """
    return web_search_service.search(query)
