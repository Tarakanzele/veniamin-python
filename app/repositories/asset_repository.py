from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset


class AssetRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, asset_id: int) -> Asset | None:
        stmt = select(Asset).where(Asset.id == asset_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_ticker(self, ticker: str) -> Asset | None:
        # Поиск по тикеру — основной способ идентификации актива в API
        stmt = select(Asset).where(Asset.ticker == ticker)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Asset]:
        # order_by сортирует результаты по алфавиту тикера
        stmt = select(Asset).order_by(Asset.ticker)
        result = await self._session.execute(stmt)
        # scalars() извлекает объекты модели из результата; all() собирает в список
        return list(result.scalars().all())

    async def create(self, ticker: str, name: str, market: str, currency: str) -> Asset:
        asset = Asset(ticker=ticker, name=name, market=market, currency=currency)
        self._session.add(asset)
        await self._session.commit()
        await self._session.refresh(asset)
        return asset

    async def update(self, asset: Asset, **fields) -> Asset:
        # Обновляем только переданные поля (частичное обновление — PATCH)
        for key, value in fields.items():
            if value is not None:  # пропускаем поля, которые не были переданы
                setattr(asset, key, value)
        await self._session.commit()
        await self._session.refresh(asset)
        return asset

    async def delete(self, asset: Asset) -> None:
        # delete помечает объект на удаление; commit выполняет DELETE в БД
        await self._session.delete(asset)
        await self._session.commit()
