from typing import Any

from langchain.tools import tool

from core.constants import constants
from service.yfinance_service import YFinanceService
from tools.decorator import register_tool


yfinance_service = YFinanceService()


def _extract_ticker(value: str) -> str:
    """
    Extract a ticker symbol from either a plain ticker or
    a natural-language query.

    Examples:
        GOLDBEES
        GOLDBEES.NS
        Current GOLDBEES stock price today
        What is the stock price of GOLDBEES?
    """

    if not value:
        raise ValueError("Ticker or query is required.")

    value = value.strip().upper()

    # If the value is already a simple ticker, return it.
    if " " not in value:
        return value

    # Remove common natural-language words.
    ignored_words = {
        "WHAT",
        "IS",
        "THE",
        "CURRENT",
        "STOCK",
        "PRICE",
        "TODAY",
        "SHARE",
        "SHARES",
        "VALUE",
        "OF",
        "FOR",
        "NOW",
        "PLEASE",
        "TELL",
        "ME",
        "LATEST",
        "MARKET",
        "RATE",
    }

    # Remove punctuation.
    cleaned = (
        value.replace("?", " ")
        .replace(",", " ")
        .replace(".", " ")
        .replace("!", " ")
        .replace(":", " ")
    )

    words = cleaned.split()

    candidates = [
        word
        for word in words
        if word not in ignored_words
    ]

    if not candidates:
        raise ValueError(
            f"Could not determine ticker from: {value}"
        )

    # For:
    # "CURRENT GOLDBEES STOCK PRICE TODAY"
    #
    # candidates = ["GOLDBEES"]
    return candidates[0]


def yfinance_impl(
    ticker: str | None = None,
    symbol: str | None = None,
    query: str | None = None,
    context: Any = None,
) -> dict[str, Any]:
    """
    Internal handler used by the tool registry.

    Supports:
        ticker="GOLDBEES"
        symbol="GOLDBEES"
        query="Current GOLDBEES stock price today"
    """

    # Prefer an explicit ticker.
    raw_value = ticker or symbol or query

    if not raw_value:
        return {
            "summary": "Please provide a stock ticker symbol.",
            "citations": [],
            "metadata": {},
        }

    try:
        normalized_ticker = _extract_ticker(raw_value)

        return yfinance_service.get_quote(normalized_ticker)

    except Exception as ex:
        return {
            "summary": f"Unable to process ticker: {str(ex)}",
            "citations": [],
            "metadata": {},
        }


@register_tool(
    name=constants.YFINANCE,
    handler=yfinance_impl,
    category=constants.GEN,
)
@tool
def yfinance_tool(
    ticker: str | None = None,
    symbol: str | None = None,
    query: str | None = None,
) -> dict[str, Any]:
    """
    Get current financial market information for a stock or ETF.

    Provide any one of:
        ticker: Yahoo Finance ticker symbol.
        symbol: Stock/ETF symbol.
        query: Natural-language request containing the ticker.

    Examples:
        ticker="AAPL"
        symbol="GOLDBEES"
        query="Current GOLDBEES stock price today"

    Returns:
        Current market information.
    """

    return yfinance_impl(
        ticker=ticker,
        symbol=symbol,
        query=query,
    )
