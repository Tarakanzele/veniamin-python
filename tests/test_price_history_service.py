from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import AssetNotFoundError
from app.models.asset import Asset
from app.models.price_history import PriceHistory
from app.services.price_history_service import PriceHistoryService


def make_service(asset: Asset | None) -> PriceHistoryService:
    asset_repo = MagicMock()
    asset_repo.get_by_ticker = AsyncMock(return_value=asset)

    price_repo = MagicMock()
    price_repo.get_by_asset = AsyncMock(return_value=[
        PriceHistory(id=1, asset_id=1, price=150.0)
    ])
    price_repo.add = AsyncMock(return_value=PriceHistory(id=2, asset_id=1, price=155.0))

    return PriceHistoryService(asset_repo, price_repo)


@pytest.mark.asyncio
async def test_get_history_success() -> None:
    asset = Asset(id=1, ticker="AAPL", name="Apple", market="NASDAQ", currency="USD")
    service = make_service(asset)
    records = await service.get_history("AAPL")
    assert len(records) == 1
    assert records[0].price == 150.0


@pytest.mark.asyncio
async def test_get_history_asset_not_found() -> None:
    service = make_service(None)
    with pytest.raises(AssetNotFoundError):
        await service.get_history("GHOST")


@pytest.mark.asyncio
async def test_add_price_success() -> None:
    asset = Asset(id=1, ticker="AAPL", name="Apple", market="NASDAQ", currency="USD")
    service = make_service(asset)
    record = await service.add_price("AAPL", 155.0)
    assert record.price == 155.0


@pytest.mark.asyncio
async def test_add_price_asset_not_found() -> None:
    service = make_service(None)
    with pytest.raises(AssetNotFoundError):
        await service.add_price("GHOST", 100.0)
