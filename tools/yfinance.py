import logging
import re
from typing import Any

from langchain.tools import tool

from core.constants import constants
from service.yfinance_service import YFinanceService
from tools.decorator import register_tool
from tools.tool_registry import ToolRisk

logger = logging.getLogger(__name__)

yfinance_service = YFinanceService()


def _extract_ticker(value: str) -> str:
    if not value or not value.strip():
        raise ValueError("A ticker or query is required.")

    value = value.strip().upper()

    if " " not in value:
        return value

    ignored_words = {
        "WHAT", "IS", "THE", "CURRENT", "STOCK", "PRICE",
        "TODAY", "SHARE", "SHARES", "VALUE", "OF", "FOR",
        "NOW", "PLEASE", "TELL", "ME", "LATEST", "MARKET",
        "RATE", "GET", "SHOW", "FIND", "QUOTE",
    }

    cleaned = re.sub(r"[?!,:;]", " ", value)
    words = cleaned.split()
    candidates = [word for word in words if word not in ignored_words]

    if not candidates:
        raise ValueError("Could not determine the ticker symbol.")

    return candidates[0]


def yfinance_impl(ticker: str | None = None, symbol: str | None = None, query: str | None = None, context: Any = None) -> dict[str, Any]:
    raw_value = ticker or symbol or query

    if not raw_value or not raw_value.strip():
        return {
            constants.SUMMARY: "Please provide a stock ticker symbol.",
            constants.CITATIONS: [],
            constants.METADATA: {
                constants.SUCC: False,
                constants.RETRYABLE: False,
            },
        }

    try:
        normalized_ticker = _extract_ticker(raw_value)
    except ValueError:
        return {
            constants.SUMMARY: (
                "Unable to identify a stock ticker. Please provide a symbol, "
                "such as AAPL or GOLDBEES.NS."
            ),
            constants.CITATIONS: [],
            constants.METADATA: {
                constants.SUCC: False,
                constants.RETRYABLE: False,
            },
        }

    try:
        return yfinance_service.get_quote(normalized_ticker)
    except Exception:
        logger.exception(
            "Unexpected finance tool failure | ticker=%s",
            normalized_ticker,
        )
        return {
            constants.SUMMARY: (
                "Unable to retrieve financial information at this time."
            ),
            constants.CITATIONS: [],
            constants.METADATA: {
                constants.TICKER: normalized_ticker,
                constants.SUCC: False,
                constants.RETRYABLE: True,
            },
        }


@register_tool(name=constants.YFINANCE, handler=yfinance_impl, category=constants.GEN, risk=ToolRisk.MEDIUM)
@tool
def yfinance_tool(
    ticker: str | None = None,
    symbol: str | None = None,
    query: str | None = None,
) -> dict[str, Any]:
    """Get market information for a stock or ETF.

    Args:
        ticker: Yahoo Finance ticker symbol.
        symbol: Stock or ETF symbol.
        query: Natural-language request containing the ticker.

    Returns:
        Structured financial information and citations.
    """
    return yfinance_impl(
        ticker=ticker,
        symbol=symbol,
        query=query,
    )
	
