from collections.abc import AsyncGenerator

# AsyncSession — асинхронная сессия SQLAlchemy для работы с БД без блокировок
# async_sessionmaker — фабрика для создания сессий
# create_async_engine — создаёт асинхронный движок подключения к PostgreSQL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# Движок подключения — создаётся один раз при старте приложения
# pool_pre_ping=True — проверяет соединение перед каждым использованием (защита от обрывов)
# echo=True выводит все SQL-запросы в лог (только в режиме DEBUG)
engine = create_async_engine(
    settings.DATABASE_URL_ASYNC,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

# Фабрика сессий — expire_on_commit=False означает, что объекты остаются
# доступными после коммита без дополнительных запросов к БД
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Генератор-зависимость для FastAPI: открывает сессию, передаёт в роут,
# автоматически закрывает после завершения запроса
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session  # yield передаёт сессию в роут, блок after yield — cleanup
