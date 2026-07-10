import asyncio

from app.core.logging import logger
from app.db.session import async_session_factory
from app.repositories.asset_repository import AssetRepository
from app.repositories.price_history_repository import PriceHistoryRepository
from app.utils.cache import cache_price
from app.utils.market.yahoo_provider import YahooMarketProvider
from app.utils.ws_manager import ws_manager
from app.workers.celery_app import celery_app


# bind=True — задача получает self (ссылку на себя) для повторных попыток
# max_retries=3 — при ошибке попробует ещё 3 раза перед тем как упасть
@celery_app.task(name="tasks.fetch_prices", bind=True, max_retries=3)
def fetch_prices(self) -> None:
    # Celery Worker работает синхронно, поэтому запускаем async-функцию через asyncio.run
    asyncio.run(_fetch_prices_async())


async def _fetch_prices_async() -> None:
    provider = YahooMarketProvider()
    # Создаём новую сессию БД для этой задачи (не используем сессию из FastAPI)
    async with async_session_factory() as session:
        asset_repo = AssetRepository(session)
        price_repo = PriceHistoryRepository(session)

        # Получаем список всех активов, за которыми следим
        assets = await asset_repo.get_all()
        if not assets:
            logger.info("No assets to fetch prices for")
            return

        # Собираем список тикеров для пакетного запроса
        tickers = [a.ticker for a in assets]
        try:
            # Запрашиваем цены всех тикеров за один раз
            prices = await provider.get_prices(tickers)
        except Exception as exc:
            logger.error("Price fetch failed: %s", exc)
            return

        for asset in assets:
            price = prices.get(asset.ticker)
            if price is not None:
                # Сохраняем цену в историю PostgreSQL
                await price_repo.add(asset.id, price)
                # Кешируем в Redis для быстрого доступа через GET /assets/{ticker}/price
                await cache_price(asset.ticker, price)
                # Рассылаем WebSocket-клиентам, подписанным на этот тикер
                await ws_manager.broadcast(asset.ticker, price)

        logger.info("Fetched and saved prices for %d assets", len(prices))
