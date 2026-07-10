from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import AssetNotFoundError
from app.models.asset import Asset
from app.models.price_history import PriceHistory
from app.services.analytics_service import AnalyticsService


def make_service(asset=None, prices=None):
    asset_repo = MagicMock()
    asset_repo.get_by_ticker = AsyncMock(return_value=asset)

    price_repo = MagicMock()
    price_repo.get_by_asset = AsyncMock(return_value=prices or [])

    return AnalyticsService(asset_repo, price_repo)


@pytest.mark.asyncio
async def test_analytics_no_asset() -> None:
    service = make_service(asset=None)
    with pytest.raises(AssetNotFoundError):
        await service.get_asset_analytics("GHOST")


@pytest.mark.asyncio
async def test_analytics_no_prices() -> None:
    asset = Asset(id=1, ticker="AAPL", name="Apple", market="NASDAQ", currency="USD")
    service = make_service(asset=asset, prices=[])
    with pytest.raises(AssetNotFoundError):
        await service.get_asset_analytics("AAPL")


@pytest.mark.asyncio
async def test_analytics_correct_values() -> None:
    asset = Asset(id=1, ticker="AAPL", name="Apple", market="NASDAQ", currency="USD")
    prices = [
        PriceHistory(id=3, asset_id=1, price=150.0),
        PriceHistory(id=2, asset_id=1, price=140.0),
        PriceHistory(id=1, asset_id=1, price=100.0),
    ]
    service = make_service(asset=asset, prices=prices)
    result = await service.get_asset_analytics("AAPL")

    assert result.current_price == 150.0
    assert result.min_price == 100.0
    assert result.max_price == 150.0
    assert result.avg_price == pytest.approx(130.0)
    assert result.price_change == pytest.approx(50.0)
    assert result.data_points == 3
