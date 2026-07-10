# httpx — асинхронная HTTP-библиотека (аналог requests, но с поддержкой asyncio)
import httpx

from app.core.logging import logger


class YahooMarketProvider:
    """Получает цены с Yahoo Finance через неофициальный chart API."""

    # Шаблон URL: {ticker} заменяется на конкретный тикер (например, AAPL)
    _BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"

    async def get_price(self, ticker: str) -> float:
        # Делегируем пакетному методу, передав список из одного тикера
        prices = await self.get_prices([ticker])
        return prices[ticker]

    async def get_prices(self, tickers: list[str]) -> dict[str, float]:
        results: dict[str, float] = {}
        # AsyncClient — менеджер контекста: автоматически закрывает соединения
        # timeout=10 — если API не отвечает 10 секунд, бросаем исключение
        async with httpx.AsyncClient(timeout=10) as client:
            for ticker in tickers:
                try:
                    url = self._BASE_URL.format(ticker=ticker)
                    # User-Agent нужен, иначе Yahoo может вернуть 429 Too Many Requests
                    response = await client.get(url, headers={"User-Agent": "StockWatch/1.0"})
                    # raise_for_status() бросает исключение если статус 4xx или 5xx
                    response.raise_for_status()
                    data = response.json()
                    # Путь к цене в структуре ответа Yahoo Finance API
                    price = data["chart"]["result"][0]["meta"]["regularMarketPrice"]
                    results[ticker] = float(price)
                    logger.info("Fetched price %s = %.4f", ticker, price)
                except Exception as exc:
                    logger.error("Failed to fetch price for %s: %s", ticker, exc)
                    raise
        return results
