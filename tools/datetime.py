from datetime import datetime, timezone
from tools.decorator import register_tool

from langchain.tools import tool
from core.constants import constants
from common.tool_result import ToolResult
from tools.tool_registry import ToolRisk

def date_time_impl(context=None)->ToolResult:
    return {
        constants.SUMMARY: datetime.now(timezone.utc).strftime(constants.STRF_TIME),
        constants.CITATIONS: [],
        constants.METADATA: {},
    }


@register_tool(name=constants.CUR_DT, handler=date_time_impl, category=constants.GEN, risk=ToolRisk.LOW)
@tool(parse_docstring=True)
def current_datetime() -> str:
    """
    Returns the current date and time.

    Returns:
        The current local date and time formatted as DD-MM-YYYY HH:MM:SS.
    """
    return date_time_impl()
