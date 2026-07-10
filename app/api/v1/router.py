from fastapi import APIRouter

# Импортируем все модули с роутами
from app.api.v1 import alerts, analytics, auth, assets, prices, ws

# Главный роутер с префиксом /api/v1 — все дочерние роуты наследуют этот префикс
api_router = APIRouter(prefix="/api/v1")

# Подключаем роутеры по функциональным блокам
api_router.include_router(auth.router)       # /api/v1/auth/*
api_router.include_router(assets.router)     # /api/v1/assets/*
api_router.include_router(prices.router)     # /api/v1/assets/{ticker}/prices
api_router.include_router(alerts.router)     # /api/v1/alerts/*
api_router.include_router(analytics.router)  # /api/v1/analytics/*
api_router.include_router(ws.router)         # /api/v1/ws/*
