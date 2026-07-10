from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import AssetNotFoundError
from app.models.asset import Asset
from app.services.asset_service import AssetService


def make_asset(ticker: str = "AAPL") -> Asset:
    return Asset(id=1, ticker=ticker, name="Apple Inc.", market="NASDAQ", currency="USD")


def make_service(asset: Asset | None = None) -> AssetService:
    repo = MagicMock()
    repo.get_by_ticker = AsyncMock(return_value=asset)
    repo.get_all = AsyncMock(return_value=[asset] if asset else [])
    repo.create = AsyncMock(return_value=make_asset())
    repo.update = AsyncMock(side_effect=lambda a, **kw: a)
    repo.delete = AsyncMock()
    return AssetService(repo)


@pytest.mark.asyncio
async def test_get_all_returns_list() -> None:
    service = make_service(make_asset())
    result = await service.get_all()
    assert len(result) == 1


@pytest.mark.asyncio
async def test_get_by_ticker_success() -> None:
    service = make_service(make_asset("AAPL"))
    asset = await service.get_by_ticker("aapl")
    assert asset.ticker == "AAPL"


@pytest.mark.asyncio
async def test_get_by_ticker_not_found() -> None:
    service = make_service(None)
    with pytest.raises(AssetNotFoundError):
        await service.get_by_ticker("UNKNOWN")


@pytest.mark.asyncio
async def test_create_uppercases_ticker() -> None:
    service = make_service()
    asset = await service.create("tsla", "Tesla", "NASDAQ", "usd")
    service._repo.create.assert_called_once_with(
        ticker="TSLA", name="Tesla", market="NASDAQ", currency="USD"
    )


@pytest.mark.asyncio
async def test_delete_not_found_raises() -> None:
    service = make_service(None)
    with pytest.raises(AssetNotFoundError):
        await service.delete("GHOST")
