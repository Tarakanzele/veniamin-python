from datetime import datetime

# Text — тип для длинных строк без ограничения длины
from sqlalchemy import ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class NotificationHistory(Base):
    __tablename__ = "notification_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Кому отправлено уведомление
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    # По какому алерту сработало уведомление
    alert_id: Mapped[int] = mapped_column(ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False)
    # Текст уведомления (например, "AAPL price 195.5 exceeded threshold 190.0")
    message: Mapped[str] = mapped_column(Text, nullable=False)
    # Время создания уведомления — проставляется базой данных
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    user: Mapped["User"] = relationship(back_populates="notification_history")
    alert: Mapped["Alert"] = relationship(back_populates="notification_history")
