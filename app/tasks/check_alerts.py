import asyncio

from app.core.logging import logger
from app.db.session import async_session_factory
from app.models.alert import AlertCondition
from app.repositories.alert_repository import AlertRepository
from app.repositories.notification_history_repository import NotificationHistoryRepository
from app.repositories.price_history_repository import PriceHistoryRepository
from app.workers.celery_app import celery_app


@celery_app.task(name="tasks.check_alerts", bind=True, max_retries=3)
def check_alerts(self) -> None:
    asyncio.run(_check_alerts_async())


async def _check_alerts_async() -> None:
    async with async_session_factory() as session:
        alert_repo = AlertRepository(session)
        price_repo = PriceHistoryRepository(session)
        notif_repo = NotificationHistoryRepository(session)

        # Берём только активные алерты (enabled=True) — неактивные пропускаем
        alerts = await alert_repo.get_enabled()
        if not alerts:
            return

        for alert in alerts:
            # Берём только самую свежую цену (limit=1)
            records = await price_repo.get_by_asset(alert.asset_id, limit=1)
            if not records:
                # Для этого актива ещё нет ни одной цены — пропускаем
                continue

            current_price = records[0].price

            # Проверяем условие срабатывания алерта
            triggered = (
                alert.condition == AlertCondition.ABOVE and current_price > alert.value
                or alert.condition == AlertCondition.BELOW and current_price < alert.value
            )

            if triggered:
                # Формируем текст уведомления
                message = (
                    f"Alert triggered: asset_id={alert.asset_id} "
                    f"price={current_price:.4f} {alert.condition.value} {alert.value:.4f}"
                )
                # Сохраняем уведомление в историю
                await notif_repo.create(alert.user_id, alert.id, message)
                # Отключаем алерт после срабатывания, чтобы не уведомлять повторно
                await alert_repo.set_enabled(alert, False)
                logger.info(message)
