# Protocol — это интерфейс в Python (утиная типизация без наследования)
# Любой класс, реализующий эти методы, считается MarketProvider
from typing import Protocol


class MarketProvider(Protocol):
    # Получить текущую цену одного актива по тикеру (например, "AAPL")
    async def get_price(self, ticker: str) -> float: ...

    # Получить цены сразу нескольких активов — возвращает словарь {ticker: price}
    async def get_prices(self, tickers: list[str]) -> dict[str, float]: ...
