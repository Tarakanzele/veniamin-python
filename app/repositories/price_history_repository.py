from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.price_history import PriceHistory


class PriceHistoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_asset(self, asset_id: int, limit: int = 100) -> list[PriceHistory]:
        stmt = (
            select(PriceHistory)
            .where(PriceHistory.asset_id == asset_id)
            # desc() — сортировка от новых к старым, чтобы первый элемент = текущая цена
            .order_by(PriceHistory.timestamp.desc())
            # limit ограничивает количество возвращаемых записей
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def add(self, asset_id: int, price: float) -> PriceHistory:
        # Создаём новую запись о цене; timestamp проставит PostgreSQL через server_default
        record = PriceHistory(asset_id=asset_id, price=price)
        self._session.add(record)
        await self._session.commit()
        await self._session.refresh(record)
        return record
