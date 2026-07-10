from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.logging import logger
from app.utils.ws_manager import ws_manager

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/prices/{ticker}")
async def price_feed(ticker: str, websocket: WebSocket) -> None:
    await ws_manager.connect(ticker, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(ticker, websocket)
        logger.info("WS disconnected: ticker=%s", ticker)
