from app.core.exceptions import AssetNotFoundError
from app.repositories.asset_repository import AssetRepository
from app.repositories.price_history_repository import PriceHistoryRepository
from app.schemas.analytics import AssetAnalyticsResponse


class AnalyticsService:
    def __init__(self, asset_repo: AssetRepository, price_repo: PriceHistoryRepository) -> None:
        self._asset_repo = asset_repo
        self._price_repo = price_repo

    async def get_asset_analytics(self, ticker: str, limit: int = 100) -> AssetAnalyticsResponse:
        asset = await self._asset_repo.get_by_ticker(ticker.upper())
        if not asset:
            raise AssetNotFoundError(f"Asset '{ticker}' not found")

        records = await self._price_repo.get_by_asset(asset.id, limit)
        if not records:
            raise AssetNotFoundError(f"No price data for '{ticker}'")

        prices = [r.price for r in records]
        current = prices[0]
        oldest = prices[-1]
        change = current - oldest
        change_pct = (change / oldest * 100) if oldest != 0 else 0.0

        return AssetAnalyticsResponse(
            ticker=asset.ticker,
            current_price=current,
            min_price=min(prices),
            max_price=max(prices),
            avg_price=sum(prices) / len(prices),
            price_change=change,
            price_change_pct=round(change_pct, 4),
            data_points=len(prices),
        )
