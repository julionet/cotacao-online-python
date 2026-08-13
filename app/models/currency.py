import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Currency(Base):
    """Moeda disponível para cotação (ex.: par USD-BRL).

    O campo `id` é uma string (e não UUID) pois representa o
    identificador do registro na fonte de dados de câmbio,
    conforme o schema `CurrencyResponse` do OpenAPI (ex.: "recFTu2BE9PnKgJ4u").
    """

    __tablename__ = "currencies"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: uuid.uuid4().hex)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    code: Mapped[str] = mapped_column(String(10), nullable=False)
    codein: Mapped[str] = mapped_column(String(10), nullable=False)
    last_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
