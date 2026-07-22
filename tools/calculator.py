from langchain.tools import tool
from tools.decorator import register_tool
from core.constants import constants
from numexpr import evaluate

@register_tool(name=constants.CALC, category=constants.UTLTY)
@tool(parse_docstring=True)
def calculator_tool(expr: str) -> str:
    """
    Evaluate a mathematical expression.

    Args:
        expr: Mathematical expression to evaluate.

    Returns:
        The evaluated result as a string.
    """
    try:
        result = evaluate(expr)

        return str(result)
    
    except Exception as e:
        return str(e)
