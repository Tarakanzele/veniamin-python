from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PriceHistory(Base):
    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    # К какому активу относится эта запись о цене
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    # Зафиксированная цена в момент timestamp
    price: Mapped[float] = mapped_column(nullable=False)
    # index=True — индекс по времени ускоряет выборку истории за период
    # server_default=func.now() — PostgreSQL проставляет время автоматически
    timestamp: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False, index=True)

    # Обратная связь: позволяет обратиться к активу через price_record.asset
    asset: Mapped["Asset"] = relationship(back_populates="price_history")
