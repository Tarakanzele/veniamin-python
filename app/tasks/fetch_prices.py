import asyncio

from app.core.logging import logger
from app.db.session import async_session_factory
from app.repositories.asset_repository import AssetRepository
from app.repositories.price_history_repository import PriceHistoryRepository
from app.utils.market.yahoo_provider import YahooMarketProvider
from app.workers.celery_app import celery_app


@celery_app.task(name="tasks.fetch_prices", bind=True, max_retries=3)
def fetch_prices(self) -> None:
    asyncio.run(_fetch_prices_async())


async def _fetch_prices_async() -> None:
    provider = YahooMarketProvider()
    async with async_session_factory() as session:
        asset_repo = AssetRepository(session)
        price_repo = PriceHistoryRepository(session)

        assets = await asset_repo.get_all()
        if not assets:
            logger.info("No assets to fetch prices for")
            return

        tickers = [a.ticker for a in assets]
        try:
            prices = await provider.get_prices(tickers)
        except Exception as exc:
            logger.error("Price fetch failed: %s", exc)
            return

        for asset in assets:
            price = prices.get(asset.ticker)
            if price is not None:
                await price_repo.add(asset.id, price)

        logger.info("Fetched and saved prices for %d assets", len(prices))
