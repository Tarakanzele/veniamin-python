from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.logging import logger
from app.utils.ws_manager import ws_manager

router = APIRouter(prefix="/ws", tags=["websocket"])


# WebSocket-эндпоинт — клиент подключается один раз и получает сообщения в реальном времени
@router.websocket("/prices/{ticker}")
async def price_feed(ticker: str, websocket: WebSocket) -> None:
    # Принимаем соединение и регистрируем клиента для данного тикера
    await ws_manager.connect(ticker, websocket)
    try:
        # Бесконечный цикл: держим соединение открытым, ожидая сообщений от клиента
        # (клиент может ничего не отправлять — мы просто слушаем)
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        # Клиент закрыл соединение — убираем его из списка подписчиков
        ws_manager.disconnect(ticker, websocket)
        logger.info("WS disconnected: ticker=%s", ticker)
