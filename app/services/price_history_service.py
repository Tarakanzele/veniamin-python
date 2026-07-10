from app.core.exceptions import AssetNotFoundError
from app.core.logging import logger
from app.models.price_history import PriceHistory
from app.repositories.asset_repository import AssetRepository
from app.repositories.price_history_repository import PriceHistoryRepository


class PriceHistoryService:
    def __init__(self, asset_repo: AssetRepository, price_repo: PriceHistoryRepository) -> None:
        self._asset_repo = asset_repo
        self._price_repo = price_repo

    async def get_history(self, ticker: str, limit: int = 100) -> list[PriceHistory]:
        asset = await self._asset_repo.get_by_ticker(ticker.upper())
        if not asset:
            raise AssetNotFoundError(f"Asset '{ticker}' not found")
        return await self._price_repo.get_by_asset(asset.id, limit)

    async def add_price(self, ticker: str, price: float) -> PriceHistory:
        asset = await self._asset_repo.get_by_ticker(ticker.upper())
        if not asset:
            raise AssetNotFoundError(f"Asset '{ticker}' not found")
        record = await self._price_repo.add(asset.id, price)
        logger.info("Price recorded: %s = %.4f", ticker.upper(), price)
        return record
