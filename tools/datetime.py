from datetime import datetime

from langchain.tools import tool
from core.constants import constants


@tool(parse_docstring=True)
def current_datetime() -> str:
    """
    Returns the current date and time.

    Returns:
        The current local date and time formatted as DD-MM-YYYY HH:MM:SS.
    """
    return datetime.now().strftime(constants.STRF_TIME)
