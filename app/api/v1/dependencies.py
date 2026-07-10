from fastapi import Depends, HTTPException, status
# HTTPBearer извлекает Bearer токен из заголовка Authorization
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import get_session
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService

# Схема авторизации: ожидает заголовок вида "Authorization: Bearer <token>"
bearer_scheme = HTTPBearer()


# Фабричные функции для Depends — создают репозиторий/сервис с нужной сессией
def get_user_repository(session: AsyncSession = Depends(get_session)) -> UserRepository:
    return UserRepository(session)


def get_auth_service(repo: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(repo)


async def get_current_user(
    # FastAPI автоматически извлекает токен из заголовка через bearer_scheme
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    repo: UserRepository = Depends(get_user_repository),
) -> User:
    try:
        # Декодируем токен и получаем user_id из поля sub
        user_id = int(decode_access_token(credentials.credentials))
    except (ValueError, TypeError):
        # Невалидный токен — возвращаем 401 Unauthorized
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # Проверяем, что пользователь с таким id действительно существует в БД
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
