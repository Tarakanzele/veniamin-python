import enum

from sqlalchemy import ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AlertCondition(str, enum.Enum):
    ABOVE = "above"
    BELOW = "below"


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    condition: Mapped[AlertCondition] = mapped_column(SAEnum(AlertCondition), nullable=False)
    value: Mapped[float] = mapped_column(nullable=False)
    enabled: Mapped[bool] = mapped_column(default=True, nullable=False)

    user: Mapped["User"] = relationship(back_populates="alerts")
    asset: Mapped["Asset"] = relationship(back_populates="alerts")
    notification_history: Mapped[list["NotificationHistory"]] = relationship(back_populates="alert", cascade="all, delete-orphan")
