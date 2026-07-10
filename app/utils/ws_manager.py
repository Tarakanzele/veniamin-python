import asyncio
import json

from fastapi import WebSocket

from app.core.logging import logger


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[str, list[WebSocket]] = {}

    async def connect(self, ticker: str, ws: WebSocket) -> None:
        await ws.accept()
        self._connections.setdefault(ticker.upper(), []).append(ws)
        logger.info("WS client connected: ticker=%s total=%d", ticker, len(self._connections[ticker.upper()]))

    def disconnect(self, ticker: str, ws: WebSocket) -> None:
        clients = self._connections.get(ticker.upper(), [])
        if ws in clients:
            clients.remove(ws)
        logger.info("WS client disconnected: ticker=%s", ticker)

    async def broadcast(self, ticker: str, price: float) -> None:
        clients = self._connections.get(ticker.upper(), [])
        if not clients:
            return
        payload = json.dumps({"ticker": ticker.upper(), "price": price})
        dead: list[WebSocket] = []
        for ws in clients:
            try:
                await ws.send_text(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ticker, ws)


ws_manager = ConnectionManager()
