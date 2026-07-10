import enum

# ForeignKey — внешний ключ, ссылается на строку в другой таблице
# Enum as SAEnum — тип перечисления на уровне базы данных
from sqlalchemy import ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


# Условие срабатывания алерта: цена выше или ниже заданного значения
class AlertCondition(str, enum.Enum):
    ABOVE = "above"  # сработает, если цена поднимется выше value
    BELOW = "below"  # сработает, если цена опустится ниже value


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    # ondelete="CASCADE" — при удалении пользователя удаляются его алерты на уровне БД
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    # Алерт привязан к конкретному активу
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    # Условие хранится как enum в PostgreSQL — защита от некорректных значений
    condition: Mapped[AlertCondition] = mapped_column(SAEnum(AlertCondition), nullable=False)
    # Пороговое значение цены для срабатывания
    value: Mapped[float] = mapped_column(nullable=False)
    # Флаг активности: False — алерт уже сработал или отключён пользователем
    enabled: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Связи позволяют обращаться к user и asset через alert.user, alert.asset
    user: Mapped["User"] = relationship(back_populates="alerts")
    asset: Mapped["Asset"] = relationship(back_populates="alerts")
    notification_history: Mapped[list["NotificationHistory"]] = relationship(back_populates="alert", cascade="all, delete-orphan")
