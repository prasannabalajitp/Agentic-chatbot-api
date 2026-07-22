from datetime import datetime
from tools.decorator import register_tool

from langchain.tools import tool
from core.constants import constants


@register_tool(name=constants.CUR_DT, category=constants.GEN)
@tool(parse_docstring=True)
def current_datetime() -> str:
    """
    Returns the current date and time.

    Returns:
        The current local date and time formatted as DD-MM-YYYY HH:MM:SS.
    """
    return datetime.now().strftime(constants.STRF_TIME)
