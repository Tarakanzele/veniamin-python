from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import StockWatchError
from app.core.logging import setup_logging, logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()
    logger.info("StockWatch starting up")
    yield
    logger.info("StockWatch shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    description="Сервис мониторинга финансовых активов",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(api_router)


@app.exception_handler(StockWatchError)
async def stockwatch_exception_handler(
    request: Request, exc: StockWatchError
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
