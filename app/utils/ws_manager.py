import asyncio
import json

from fastapi import WebSocket

from app.core.logging import logger


class ConnectionManager:
    def __init__(self) -> None:
        # Словарь: тикер → список WebSocket-соединений подписчиков
        # Один тикер может слушать несколько клиентов одновременно
        self._connections: dict[str, list[WebSocket]] = {}

    async def connect(self, ticker: str, ws: WebSocket) -> None:
        # accept() завершает WebSocket-рукопожатие и открывает соединение
        await ws.accept()
        # setdefault создаёт пустой список для нового тикера, если его нет
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
            return  # никто не подписан — ничего не делаем

        # Формируем JSON-сообщение для отправки клиентам
        payload = json.dumps({"ticker": ticker.upper(), "price": price})
        dead: list[WebSocket] = []

        for ws in clients:
            try:
                # Отправляем текстовое сообщение каждому подписчику
                await ws.send_text(payload)
            except Exception:
                # Соединение разорвано — помечаем для удаления
                dead.append(ws)

        # Убираем мёртвые соединения после итерации (нельзя менять список в процессе)
        for ws in dead:
            self.disconnect(ticker, ws)


# Глобальный экземпляр менеджера — живёт всё время работы приложения
ws_manager = ConnectionManager()
