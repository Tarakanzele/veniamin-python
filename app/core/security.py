from datetime import datetime, timedelta, timezone

# jwt — библиотека для создания и проверки JWT токенов
from jose import JWTError, jwt
# CryptContext управляет хешированием паролей
from passlib.context import CryptContext

from app.core.config import settings

# Контекст хеширования: используем bcrypt — надёжный алгоритм для паролей
# deprecated="auto" — автоматически помечает устаревшие хеши для перехеширования
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    # Возвращает bcrypt-хеш пароля для сохранения в базе данных
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    # Сравнивает введённый пароль с хешем из БД (bcrypt безопасно сравнивает)
    return pwd_context.verify(plain, hashed)


def create_access_token(subject: str | int) -> str:
    # Вычисляем момент истечения токена относительно текущего UTC-времени
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # payload — тело токена: sub (subject) — идентификатор пользователя, exp — срок действия
    payload = {"sub": str(subject), "exp": expire}
    # Подписываем токен секретным ключом — без ключа токен нельзя подделать
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> str:
    try:
        # Проверяем подпись и срок действия токена
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        # Извлекаем идентификатор пользователя из поля sub
        sub: str | None = payload.get("sub")
        if sub is None:
            raise ValueError("Token has no subject")
        return sub
    except JWTError as exc:
        # JWTError возникает при неверной подписи или истёкшем сроке
        raise ValueError("Invalid token") from exc
