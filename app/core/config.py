from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "StockWatch"
    DEBUG: bool = False

    DATABASE_URL: str
    DATABASE_URL_ASYNC: str

    REDIS_URL: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str


settings = Settings()
