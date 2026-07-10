from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "stockwatch",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.fetch_prices", "app.tasks.check_alerts"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "fetch-prices-every-5-minutes": {
            "task": "tasks.fetch_prices",
            "schedule": 300.0,
        },
        "check-alerts-every-5-minutes": {
            "task": "tasks.check_alerts",
            "schedule": 300.0,
        },
    },
)
