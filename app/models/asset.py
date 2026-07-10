from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Asset(Base):
    # Имя таблицы в базе данных
    __tablename__ = "assets"

    # Уникальный идентификатор актива
    id: Mapped[int] = mapped_column(primary_key=True)
    # Тикер (биржевой символ): AAPL, BTC, SPY — уникален и индексируется
    ticker: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    # Полное название актива: "Apple Inc.", "Bitcoin"
    name: Mapped[str] = mapped_column(nullable=False)
    # Биржа или рынок: NASDAQ, NYSE, CRYPTO
    market: Mapped[str] = mapped_column(nullable=False)
    # Валюта котировки: USD, EUR, RUB
    currency: Mapped[str] = mapped_column(nullable=False)

    # Один актив может быть в нескольких алертах разных пользователей
    alerts: Mapped[list["Alert"]] = relationship(back_populates="asset", cascade="all, delete-orphan")
    # История всех зафиксированных цен актива
    price_history: Mapped[list["PriceHistory"]] = relationship(back_populates="asset", cascade="all, delete-orphan")
