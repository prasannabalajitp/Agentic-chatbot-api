from datetime import datetime
from tools.decorator import register_tool

from langchain.tools import tool
from core.constants import constants
from common.tool_result import ToolResult

def date_time_impl(context=None)->ToolResult:
    return {
        "summary": datetime.now().strftime(constants.STRF_TIME),
        "citations": [],
        "metadata": {},
    }


@register_tool(name=constants.CUR_DT, handler=date_time_impl, category=constants.GEN)
@tool(parse_docstring=True)
def current_datetime() -> str:
    """
    Returns the current date and time.

    Returns:
        The current local date and time formatted as DD-MM-YYYY HH:MM:SS.
    """
    return date_time_impl()
