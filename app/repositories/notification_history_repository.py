from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification_history import NotificationHistory


class NotificationHistoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_user(self, user_id: int, limit: int = 50) -> list[NotificationHistory]:
        stmt = (
            select(NotificationHistory)
            .where(NotificationHistory.user_id == user_id)
            # Новые уведомления идут первыми
            .order_by(NotificationHistory.created_at.desc())
            # Ограничиваем количество, чтобы не перегружать ответ
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, user_id: int, alert_id: int, message: str) -> NotificationHistory:
        record = NotificationHistory(user_id=user_id, alert_id=alert_id, message=message)
        self._session.add(record)
        await self._session.commit()
        await self._session.refresh(record)
        return record
