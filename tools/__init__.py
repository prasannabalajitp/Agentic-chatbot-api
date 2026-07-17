from .calculator import calculator_tool
from .datetime import current_datetime
from .weather import get_weather
from .websearch import web_search
from .ai_search import ai_search

TOOLS = [
    calculator_tool,
    current_datetime,
    get_weather,
    web_search,
    ai_search
]
