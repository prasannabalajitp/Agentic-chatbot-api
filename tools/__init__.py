from .calculator import calculator_tool
from .datetime import current_datetime
from .websearch import web_search
from .ai_search import ai_search

TOOLS = [
    calculator_tool,
    current_datetime,
    web_search,
    ai_search
]
