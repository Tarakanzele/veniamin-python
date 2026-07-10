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

        alerts = await alert_repo.get_enabled()
        if not alerts:
            return

        for alert in alerts:
            records = await price_repo.get_by_asset(alert.asset_id, limit=1)
            if not records:
                continue

            current_price = records[0].price
            triggered = (
                alert.condition == AlertCondition.ABOVE and current_price > alert.value
                or alert.condition == AlertCondition.BELOW and current_price < alert.value
            )

            if triggered:
                message = (
                    f"Alert triggered: asset_id={alert.asset_id} "
                    f"price={current_price:.4f} {alert.condition.value} {alert.value:.4f}"
                )
                await notif_repo.create(alert.user_id, alert.id, message)
                await alert_repo.set_enabled(alert, False)
                logger.info(message)
