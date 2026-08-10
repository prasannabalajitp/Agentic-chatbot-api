import yfinance as yf

from core.constants import constants


class YFinanceService:

    def __init__(self):
        pass

    def _normalize_ticker(self, ticker: str) -> str:
        """
        Normalize ticker symbols for Yahoo Finance.

        GOLDBEES is an NSE-listed ETF, so Yahoo Finance uses:
            GOLDBEES.NS
        """

        ticker = ticker.upper().strip()

        # Known Indian NSE symbols that are commonly supplied
        # without the Yahoo Finance suffix.
        if ticker == "GOLDBEES":
            return "GOLDBEES.NS"

        return ticker

    def get_quote(self, ticker: str) -> dict:
        try:
            if not ticker:
                return {
                    "summary": "No ticker was provided.",
                    "citations": [],
                    "metadata": {},
                }

            ticker = self._normalize_ticker(ticker)

            stock = yf.Ticker(ticker)

            info = stock.fast_info

            last_price = info.get(constants.LP_PRICE)
            previous_close = info.get(constants.PRV_CLS)
            currency = info.get(constants.CURRNCY)

            if last_price is None:
                return {
                    "summary": (
                        f"No current price found for {ticker}."
                    ),
                    "citations": [
                        {
                            constants.TITLE: "Yahoo Finance",
                            constants.URL:
                                f"https://finance.yahoo.com/quote/{ticker}/",
                        }
                    ],
                    "metadata": {
                        "ticker": ticker,
                    },
                }

            summary = (
                f"{ticker} current price: "
                f"{last_price} {currency or ''}"
            ).strip()

            return {
                "summary": summary,
                "citations": [
                    {
                        constants.TITLE: "Yahoo Finance",
                        constants.URL:
                            f"https://finance.yahoo.com/quote/{ticker}/",
                    }
                ],
                "metadata": {
                    "ticker": ticker,
                    "price": float(last_price),
                    "previous_close": (
                        float(previous_close)
                        if previous_close is not None
                        else None
                    ),
                    "currency": currency,
                },
            }

        except Exception as ex:
            return {
                "summary": (
                    f"YFinance failed for {ticker}: {str(ex)}"
                ),
                "citations": [],
                "metadata": {},
            }

    def search(self, ticker: str) -> dict:
        return self.get_quote(ticker)
