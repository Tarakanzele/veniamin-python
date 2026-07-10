from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.dependencies import get_auth_service, get_current_user
from app.core.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from app.models.user import User
from app.schemas.user import LoginRequest, TokenResponse, UserCreate, UserResponse
from app.services.auth_service import AuthService

# prefix — общий префикс для всех роутов в этом файле
# tags — группировка в Swagger UI
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: UserCreate,  # FastAPI автоматически парсит и валидирует тело запроса
    service: AuthService = Depends(get_auth_service),  # внедряем сервис через DI
) -> UserResponse:
    try:
        user = await service.register(body.email, body.password)
    except UserAlreadyExistsError as exc:
        # Доменное исключение превращаем в HTTP 409 Conflict
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    # model_validate создаёт Pydantic-схему из ORM-объекта (from_attributes=True)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    try:
        return await service.login(body.email, body.password)
    except InvalidCredentialsError as exc:
        # 401 Unauthorized — неверные учётные данные
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))


@router.get("/me", response_model=UserResponse)
async def me(
    # get_current_user — зависимость, которая проверяет JWT и возвращает пользователя
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    return UserResponse.model_validate(current_user)
