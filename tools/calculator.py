import logging

from langchain.tools import tool
from numexpr import evaluate

from common.tool_result import ToolResult
from core.constants import constants
from tools.decorator import register_tool
from tools.tool_registry import ToolRisk

logger = logging.getLogger(__name__)


def calculator_impl(expr: str, context=None) -> ToolResult:
    if not expr or not expr.strip():
        return {
            constants.SUMMARY: "Please provide a mathematical expression.",
            constants.CITATIONS: [],
            constants.METADATA: {
                constants.SUCC: False,
                constants.RETRYABLE: False,
            },
        }

    try:
        result = evaluate(expr)
        return {
            constants.SUMMARY: str(result),
            constants.CITATIONS: [],
            constants.METADATA: {
                constants.SUCC: True,
            },
        }
    except (SyntaxError, ValueError, TypeError, KeyError, NameError):
        return {
            constants.SUMMARY: "Unable to evaluate that expression. Check its syntax and try again.",
            constants.CITATIONS: [],
            constants.METADATA: {
                constants.SUCC: False,
                constants.RETRYABLE: False,
            },
        }
    except Exception:
        return {
            constants.SUMMARY: "The calculator could not complete the request.",
            constants.CITATIONS: [],
            constants.METADATA: {
                constants.SUCC: False,
                constants.RETRYABLE: False,
            },
        }


@register_tool(name=constants.CALC, handler=calculator_impl, category=constants.UTLTY, risk=ToolRisk.LOW)
@tool(parse_docstring=True)
def calculator_tool(expr: str) -> str:
    """Evaluate a mathematical expression.

    Args:
        expr: Mathematical expression to evaluate.

    Returns:
        The evaluated result as a string.
    """
    result = calculator_impl(expr=expr)
    return result[constants.SUMMARY]
