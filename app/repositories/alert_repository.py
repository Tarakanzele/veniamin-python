from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert, AlertCondition


class AlertRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, alert_id: int) -> Alert | None:
        stmt = select(Alert).where(Alert.id == alert_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: int) -> list[Alert]:
        # Возвращает все алерты конкретного пользователя
        stmt = select(Alert).where(Alert.user_id == user_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_enabled(self) -> list[Alert]:
        # Возвращает только активные алерты — используется в Celery-задаче проверки
        stmt = select(Alert).where(Alert.enabled.is_(True))
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, user_id: int, asset_id: int, condition: AlertCondition, value: float) -> Alert:
        alert = Alert(user_id=user_id, asset_id=asset_id, condition=condition, value=value)
        self._session.add(alert)
        await self._session.commit()
        await self._session.refresh(alert)
        return alert

    async def set_enabled(self, alert: Alert, enabled: bool) -> Alert:
        # Включает или отключает алерт без удаления из базы
        alert.enabled = enabled
        await self._session.commit()
        await self._session.refresh(alert)
        return alert

    async def delete(self, alert: Alert) -> None:
        await self._session.delete(alert)
        await self._session.commit()
