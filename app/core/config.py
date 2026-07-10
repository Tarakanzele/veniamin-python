# pydantic-settings читает переменные из .env файла и валидирует их типы
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # SettingsConfigDict указывает, из какого файла читать переменные окружения
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Название приложения — используется в заголовке Swagger UI
    APP_NAME: str = "StockWatch"
    # Режим отладки: включает подробные SQL-запросы в логах
    DEBUG: bool = False

    # URL для синхронного подключения к PostgreSQL (используется в Alembic)
    DATABASE_URL: str
    # URL для асинхронного подключения (используется в FastAPI через asyncpg)
    DATABASE_URL_ASYNC: str

    # Адрес Redis — используется для кеша и как брокер Celery
    REDIS_URL: str

    # Секретный ключ для подписи JWT токенов — должен быть длинным случайным значением
    SECRET_KEY: str
    # Алгоритм подписи JWT
    ALGORITHM: str = "HS256"
    # Время жизни access-токена в минутах
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # URL брокера сообщений для Celery (Redis, отдельная база)
    CELERY_BROKER_URL: str
    # URL для хранения результатов задач Celery
    CELERY_RESULT_BACKEND: str


# Единственный экземпляр настроек — импортируется во всех модулях
settings = Settings()
