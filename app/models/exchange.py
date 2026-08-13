import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Exchange(Base):
    """Cotação (bid/ask) de um par de moedas.

    Conforme o schema `ExchangeResponse` do OpenAPI, expõe apenas
    `name`, `bid` e `ask`. `id` e `updated_at` são de uso interno,
    o segundo controlando quando o par foi sincronizado por último
    via POST /v1/exchanges/sync.
    """

    __tablename__ = "exchanges"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    bid: Mapped[float] = mapped_column(Float, nullable=False)
    ask: Mapped[float] = mapped_column(Float, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
