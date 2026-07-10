import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.db.base import Base
import app.models  # noqa: F401 — импорт регистрирует все модели в Base.metadata

# context — объект Alembic, через который управляем миграциями
config = context.config
# Устанавливаем URL БД из настроек приложения (не хардкодим в alembic.ini)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL_ASYNC)

# Настраиваем логгер из секции [loggers] в alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# target_metadata — метаданные всех таблиц: Alembic сравнивает их с реальной БД
# и генерирует нужные ALTER/CREATE/DROP команды
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    # Offline-режим: генерирует SQL-скрипт без реального подключения к БД
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    # Выполняем миграции в рамках существующего соединения
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    # Online-режим: подключаемся к реальной БД и применяем миграции
    # NullPool — не держим пул соединений (Alembic запускается разово)
    connectable = create_async_engine(
        settings.DATABASE_URL_ASYNC,
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        # run_sync позволяет выполнить синхронную функцию внутри async-контекста
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


# Выбираем режим выполнения в зависимости от аргументов Alembic
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
