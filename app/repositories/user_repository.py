# select — строит SELECT-запрос в стиле SQLAlchemy 2.0
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    # Репозиторий получает сессию через конструктор (Dependency Injection)
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: int) -> User | None:
        # Строим запрос: SELECT * FROM users WHERE id = user_id
        stmt = select(User).where(User.id == user_id)
        # execute выполняет запрос, scalar_one_or_none возвращает объект или None
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        # Поиск пользователя по email — используется при логине и проверке дублей
        stmt = select(User).where(User.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, email: str, password_hash: str) -> User:
        # Создаём объект модели — он ещё не в базе
        user = User(email=email, password_hash=password_hash)
        # add добавляет объект в сессию (помечает как "новый")
        self._session.add(user)
        # commit сохраняет изменения в базе и фиксирует транзакцию
        await self._session.commit()
        # refresh обновляет объект из базы (получаем id и created_at, заполненные БД)
        await self._session.refresh(user)
        return user
