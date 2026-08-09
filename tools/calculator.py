from langchain.tools import tool
from tools.decorator import register_tool
from core.constants import constants
from common.tool_result import ToolResult
from numexpr import evaluate

def calculator_impl(expr: str, context=None)->ToolResult:
    try:
        result = evaluate(expr)
        return {
            "summary": str(result),
            "citations": [],
            "metadata": {}
        }
    except Exception as ex:
        return {
            "summary": str(ex),
            "citations": [],
            "metadata": {},
        }

@register_tool(name=constants.CALC, handler=calculator_impl, category=constants.UTLTY)
@tool(parse_docstring=True)
def calculator_tool(expr: str) -> str:
    """
    Evaluate a mathematical expression.

    Args:
        expr: Mathematical expression to evaluate.

    Returns:
        The evaluated result as a string.
    """
    return calculator_impl(expr=expr)
