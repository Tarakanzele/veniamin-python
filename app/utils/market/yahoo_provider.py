import httpx

from app.core.logging import logger


class YahooMarketProvider:
    """Fetches prices from Yahoo Finance unofficial quote endpoint."""

    _BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"

    async def get_price(self, ticker: str) -> float:
        prices = await self.get_prices([ticker])
        return prices[ticker]

    async def get_prices(self, tickers: list[str]) -> dict[str, float]:
        results: dict[str, float] = {}
        async with httpx.AsyncClient(timeout=10) as client:
            for ticker in tickers:
                try:
                    url = self._BASE_URL.format(ticker=ticker)
                    response = await client.get(url, headers={"User-Agent": "StockWatch/1.0"})
                    response.raise_for_status()
                    data = response.json()
                    price = data["chart"]["result"][0]["meta"]["regularMarketPrice"]
                    results[ticker] = float(price)
                    logger.info("Fetched price %s = %.4f", ticker, price)
                except Exception as exc:
                    logger.error("Failed to fetch price for %s: %s", ticker, exc)
                    raise
        return results
