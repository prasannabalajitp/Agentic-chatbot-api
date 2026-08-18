import yfinance as yf
from core.constants import constants

class YFinanceService:

    def __init__(self):
        pass

    def _resolve_ticker(self, ticker: str) -> str:
        ticker = ticker.strip().upper()

        if constants.DOT in ticker:
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
            return ticker

    def get_quote(self, ticker: str) -> dict:
        try:
            if not ticker:
                return {
                    constants.SUMMARY: "No ticker was provided.",
                    constants.CITATIONS: [],
                    constants.METADATA: {},
                }

            resolved_ticker = self._resolve_ticker(ticker)

            stock = yf.Ticker(resolved_ticker)

            history = stock.history(
                period=constants.DAYS,
                auto_adjust=False,
            )

            if history.empty:
                return {
                    constants.SUMMARY: (
                        f"No price data found for "
                        f"{resolved_ticker}."
                    ),
                    constants.CITATIONS: [],
                    constants.METADATA: {
                        constants.TICKER: resolved_ticker,
                    },
                }

            latest = history.iloc[-1]

            last_price = latest[constants.CLS]

            previous_close = (
                history.iloc[-2][constants.CLS]
                if len(history) > 1
                else None
            )

            return {
                constants.SUMMARY: (
                    f"{resolved_ticker} current price: "
                    f"{float(last_price):.2f}"
                ),
                constants.CITATIONS: [
                    {
                        constants.TITLE: "Yahoo Finance",
                        constants.URL:
                            f"https://finance.yahoo.com/"
                            f"quote/{resolved_ticker}/",
                    }
                ],
                constants.METADATA: {
                    constants.TICKER: resolved_ticker,
                    "price": float(last_price),
                    "previous_close": (
                        float(previous_close)
                        if previous_close is not None
                        else None
                    ),
                },
            }

        except Exception as ex:
            return {
                constants.SUMMARY: (
                    f"YFinance failed for {ticker}: {str(ex)}"
                ),
                constants.CITATIONS: [],
                constants.METADATA: {},
            }
