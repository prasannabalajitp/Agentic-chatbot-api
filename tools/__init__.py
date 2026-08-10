from .calculator import calculator_tool
from .datetime import current_datetime
from .websearch import web_search
from .ai_search import ai_search
from .list_uploaded_files import list_uploaded_files
from .yfinance import yfinance_tool

TOOLS = [
    calculator_tool,
    current_datetime,
    web_search,
    ai_search,
    list_uploaded_files,
    yfinance_tool
]
