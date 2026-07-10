from app.core.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from app.core.logging import logger
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import TokenResponse


class AuthService:
    # Сервис не знает о FastAPI — только о бизнес-логике и репозитории
    def __init__(self, user_repo: UserRepository) -> None:
        self._user_repo = user_repo

    async def register(self, email: str, password: str) -> User:
        # Проверяем, не занят ли email другим пользователем
        existing = await self._user_repo.get_by_email(email)
        if existing:
            # Выбрасываем доменное исключение — роут превратит его в HTTP 409
            raise UserAlreadyExistsError(f"User with email '{email}' already exists")

        # Передаём хеш пароля, а не сам пароль — в БД никогда не хранится открытый пароль
        user = await self._user_repo.create(
            email=email,
            password_hash=hash_password(password),
        )
        logger.info("New user registered: %s (id=%d)", email, user.id)
        return user

    async def login(self, email: str, password: str) -> TokenResponse:
        # Ищем пользователя по email
        user = await self._user_repo.get_by_email(email)
        # Проверяем и существование пользователя, и пароль в одном условии
        # — это не даёт злоумышленнику понять, что именно неверно
        if not user or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password")

        # Создаём JWT токен с user.id в качестве subject
        token = create_access_token(user.id)
        logger.info("User logged in: %s (id=%d)", email, user.id)
        return TokenResponse(access_token=token)
