from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import StockWatchError
from app.core.logging import setup_logging, logger


# asynccontextmanager превращает генератор в контекстный менеджер жизненного цикла
# Код до yield — выполняется при старте приложения
# Код после yield — выполняется при остановке
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()  # инициализируем логгер до первого входящего запроса
    logger.info("StockWatch starting up")
    yield  # здесь приложение работает и обрабатывает запросы
    logger.info("StockWatch shutting down")


# Создаём приложение FastAPI
# lifespan — обработчик событий старта и остановки
app = FastAPI(
    title=settings.APP_NAME,
    description="Сервис мониторинга финансовых активов",
    version="0.1.0",
    lifespan=lifespan,
)

# Подключаем все роуты с префиксом /api/v1
app.include_router(api_router)


# Глобальный обработчик исключений — перехватывает StockWatchError из любого сервиса
# Это позволяет не писать try/except в каждом роуте для доменных ошибок
@app.exception_handler(StockWatchError)
async def stockwatch_exception_handler(
    request: Request, exc: StockWatchError
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


# Простой эндпоинт для проверки работоспособности сервиса (используется в Docker healthcheck)
@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
