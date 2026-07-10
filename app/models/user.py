from datetime import datetime

# func предоставляет SQL-функции, например func.now() → NOW() в PostgreSQL
from sqlalchemy import func
# Mapped — тип аннотации для колонок, mapped_column — описание колонки
# relationship — описывает связь между таблицами
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    # Имя таблицы в базе данных
    __tablename__ = "users"

    # Первичный ключ — уникальный идентификатор пользователя
    id: Mapped[int] = mapped_column(primary_key=True)
    # Email уникален (unique=True) и индексируется для быстрого поиска
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    # Хеш пароля — никогда не храним пароль в открытом виде
    password_hash: Mapped[str] = mapped_column(nullable=False)
    # server_default=func.now() — PostgreSQL сам проставляет текущее время при INSERT
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    # back_populates связывает оба конца отношения (User ↔ Alert)
    # cascade="all, delete-orphan" — при удалении пользователя удаляются все его алерты
    alerts: Mapped[list["Alert"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    # Аналогично для истории уведомлений
    notification_history: Mapped[list["NotificationHistory"]] = relationship(back_populates="user", cascade="all, delete-orphan")
