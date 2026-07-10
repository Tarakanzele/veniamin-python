# Celery — библиотека для выполнения задач в фоновых процессах
from celery import Celery

from app.core.config import settings

# Создаём экземпляр Celery с именем приложения
# broker — Redis, куда Celery Beat кладёт задачи для выполнения
# backend — Redis, куда Worker сохраняет результаты задач
# include — список модулей, где Celery будет искать задачи (@celery_app.task)
celery_app = Celery(
    "stockwatch",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.fetch_prices", "app.tasks.check_alerts"],
)

celery_app.conf.update(
    # Формат сериализации задач и результатов
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    # Все времена в UTC, чтобы не зависеть от часового пояса сервера
    timezone="UTC",
    enable_utc=True,
    # Расписание Celery Beat — задачи запускаются автоматически по расписанию
    beat_schedule={
        # Получать актуальные цены каждые 5 минут (300 секунд)
        "fetch-prices-every-5-minutes": {
            "task": "tasks.fetch_prices",
            "schedule": 300.0,
        },
        # Проверять условия алертов тоже каждые 5 минут
        "check-alerts-every-5-minutes": {
            "task": "tasks.check_alerts",
            "schedule": 300.0,
        },
    },
)
