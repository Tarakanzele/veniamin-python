from app.core.exceptions import AssetNotFoundError
from app.core.logging import logger
from app.models.asset import Asset
from app.repositories.asset_repository import AssetRepository


class AssetService:
    def __init__(self, repo: AssetRepository) -> None:
        self._repo = repo

    async def get_all(self) -> list[Asset]:
        # Просто делегируем репозиторию — сервис здесь не добавляет логики
        return await self._repo.get_all()

    async def get_by_ticker(self, ticker: str) -> Asset:
        # upper() — нормализуем тикер к верхнему регистру перед поиском
        asset = await self._repo.get_by_ticker(ticker.upper())
        if not asset:
            raise AssetNotFoundError(f"Asset '{ticker}' not found")
        return asset

    async def create(self, ticker: str, name: str, market: str, currency: str) -> Asset:
        # Нормализуем тикер и валюту к верхнему регистру перед сохранением
        asset = await self._repo.create(
            ticker=ticker.upper(),
            name=name,
            market=market,
            currency=currency.upper(),
        )
        logger.info("Asset created: %s", asset.ticker)
        return asset

    async def update(self, ticker: str, name: str | None, market: str | None, currency: str | None) -> Asset:
        # Сначала проверяем существование актива — чтобы не делать UPDATE по несуществующей записи
        asset = await self._repo.get_by_ticker(ticker.upper())
        if not asset:
            raise AssetNotFoundError(f"Asset '{ticker}' not found")
        # Передаём только те поля, которые нужно обновить (частичное обновление)
        updated = await self._repo.update(asset, name=name, market=market, currency=currency)
        logger.info("Asset updated: %s", ticker)
        return updated

    async def delete(self, ticker: str) -> None:
        asset = await self._repo.get_by_ticker(ticker.upper())
        if not asset:
            raise AssetNotFoundError(f"Asset '{ticker}' not found")
        await self._repo.delete(asset)
        logger.info("Asset deleted: %s", ticker)
