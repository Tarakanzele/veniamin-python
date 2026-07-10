from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.dependencies import get_current_user
from app.core.exceptions import AssetNotFoundError
from app.db.session import get_session
from app.models.user import User
from app.repositories.asset_repository import AssetRepository
from app.schemas.asset import AssetCreate, AssetResponse, AssetUpdate
from app.services.asset_service import AssetService
from app.utils.cache import get_cached_price
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/assets", tags=["assets"])


# Локальная фабрика зависимости — создаёт AssetService с репозиторием для текущей сессии
def get_asset_service(session: AsyncSession = Depends(get_session)) -> AssetService:
    return AssetService(AssetRepository(session))


@router.get("/", response_model=list[AssetResponse])
async def list_assets(
    service: AssetService = Depends(get_asset_service),
    _: User = Depends(get_current_user),  # _ означает: пользователь нужен только для авторизации
) -> list[AssetResponse]:
    assets = await service.get_all()
    # Преобразуем каждую ORM-модель в Pydantic-схему для ответа
    return [AssetResponse.model_validate(a) for a in assets]


@router.get("/{ticker}/price")
async def get_latest_price(
    ticker: str,
    service: AssetService = Depends(get_asset_service),
    _: User = Depends(get_current_user),
) -> dict:
    # Убеждаемся, что актив существует, прежде чем смотреть кеш
    try:
        await service.get_by_ticker(ticker)
    except AssetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    # Читаем последнюю цену из Redis (быстро, без обращения к PostgreSQL)
    price = await get_cached_price(ticker)
    # cached=False означает, что цена ещё не была получена от внешнего провайдера
    return {"ticker": ticker.upper(), "price": price, "cached": price is not None}


@router.get("/{ticker}", response_model=AssetResponse)
async def get_asset(
    ticker: str,
    service: AssetService = Depends(get_asset_service),
    _: User = Depends(get_current_user),
) -> AssetResponse:
    try:
        asset = await service.get_by_ticker(ticker)
    except AssetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return AssetResponse.model_validate(asset)


@router.post("/", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(
    body: AssetCreate,
    service: AssetService = Depends(get_asset_service),
    _: User = Depends(get_current_user),
) -> AssetResponse:
    asset = await service.create(body.ticker, body.name, body.market, body.currency)
    return AssetResponse.model_validate(asset)


# PATCH — частичное обновление (только переданные поля)
@router.patch("/{ticker}", response_model=AssetResponse)
async def update_asset(
    ticker: str,
    body: AssetUpdate,
    service: AssetService = Depends(get_asset_service),
    _: User = Depends(get_current_user),
) -> AssetResponse:
    try:
        asset = await service.update(ticker, body.name, body.market, body.currency)
    except AssetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return AssetResponse.model_validate(asset)


# 204 No Content — успешное удаление не возвращает тело ответа
@router.delete("/{ticker}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    ticker: str,
    service: AssetService = Depends(get_asset_service),
    _: User = Depends(get_current_user),
) -> None:
    try:
        await service.delete(ticker)
    except AssetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
