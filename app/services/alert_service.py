from app.core.exceptions import AlertNotFoundError
from app.core.logging import logger
from app.models.alert import Alert, AlertCondition
from app.repositories.alert_repository import AlertRepository


class AlertService:
    def __init__(self, repo: AlertRepository) -> None:
        self._repo = repo

    async def get_user_alerts(self, user_id: int) -> list[Alert]:
        # Возвращаем только алерты текущего пользователя — изоляция данных
        return await self._repo.get_by_user(user_id)

    async def create(self, user_id: int, asset_id: int, condition: AlertCondition, value: float) -> Alert:
        alert = await self._repo.create(user_id, asset_id, condition, value)
        logger.info("Alert created: user_id=%d asset_id=%d %s %.4f", user_id, asset_id, condition, value)
        return alert

    async def set_enabled(self, alert_id: int, user_id: int, enabled: bool) -> Alert:
        alert = await self._repo.get_by_id(alert_id)
        # Проверяем и существование алерта, и принадлежность пользователю
        # — чтобы нельзя было управлять чужими алертами, зная их id
        if not alert or alert.user_id != user_id:
            raise AlertNotFoundError(f"Alert {alert_id} not found")
        return await self._repo.set_enabled(alert, enabled)

    async def delete(self, alert_id: int, user_id: int) -> None:
        alert = await self._repo.get_by_id(alert_id)
        # Та же проверка владельца перед удалением
        if not alert or alert.user_id != user_id:
            raise AlertNotFoundError(f"Alert {alert_id} not found")
        await self._repo.delete(alert)
        logger.info("Alert deleted: id=%d user_id=%d", alert_id, user_id)
