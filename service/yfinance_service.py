import logging

import yfinance as yf

from core.constants import constants

logger = logging.getLogger(__name__)


class YFinanceService:
    def _resolve_ticker(self, ticker: str) -> str:
        ticker = ticker.strip().upper()

        if not ticker or constants.DOT in ticker:
            return ticker

        try:
            search = yf.Search(ticker)
            quotes = search.quotes

            if not quotes:
                return ticker

            for quote in quotes:
                symbol = quote.get(constants.SYMB)
                if symbol and symbol.upper() == ticker:
                    return symbol

            for quote in quotes:
                if quote.get(constants.QUOT_TYP) == constants.EQTY:
                    symbol = quote.get(constants.SYMB)
                    if symbol:
                        return symbol

            return ticker

        except Exception:
            logger.warning(
                "Ticker resolution failed | ticker=%s",
                ticker,
                exc_info=True,
            )
            return ticker

    def get_quote(self, ticker: str) -> dict:
        if not ticker or not ticker.strip():
            return {
                constants.SUMMARY: constants.NO_TCKR,
                constants.CITATIONS: [],
                constants.METADATA: {
                    constants.SUCC: False,
                    constants.RETRYABLE: False,
                },
            }

        try:
            resolved_ticker = self._resolve_ticker(ticker)
            stock = yf.Ticker(resolved_ticker)

            history = stock.history(
                period=constants.DAYS,
                auto_adjust=False,
            )

            if history.empty:
                return {
                    constants.SUMMARY: (
                        f"No price data found for {resolved_ticker}."
                    ),
                    constants.CITATIONS: [],
                    constants.METADATA: {
                        constants.TICKER: resolved_ticker,
                        constants.SUCC: True,
                    },
                }

            latest = history.iloc[-1]
            last_price = float(latest[constants.CLS])

            previous_close = (
                float(history.iloc[-2][constants.CLS])
                if len(history) > 1
                else None
            )

            return {
                constants.SUMMARY: (
                    f"{resolved_ticker} current price: {last_price:.2f}"
                ),
                constants.CITATIONS: [
                    {
                        constants.TITLE: "Yahoo Finance",
                        constants.URL: (
                            f"{constants.YFINANCE_URL}"
                            f"quote/{resolved_ticker}/"
                        ),
                    }
                ],
                constants.METADATA: {
                    constants.TICKER: resolved_ticker,
                    constants.PRICE: last_price,
                    constants.PREV_CLS: previous_close,
                    constants.SUCC: True,
                },
            }

        except Exception:
            logger.exception(
                "Yahoo Finance request failed | ticker=%s",
                ticker,
            )
            return {
                constants.SUMMARY: (
                    "Unable to retrieve financial data at this time."
                ),
                constants.CITATIONS: [],
                constants.METADATA: {
                    constants.TICKER: ticker.strip().upper(),
                    constants.SUCC: False,
                    constants.ERROR_TYPE: constants.SERVICE_ERROR,
                    constants.RETRYABLE: True,
                },
            }
