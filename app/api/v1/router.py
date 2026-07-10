from fastapi import APIRouter

from app.api.v1 import alerts, auth, assets, prices

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(assets.router)
api_router.include_router(prices.router)
api_router.include_router(alerts.router)
