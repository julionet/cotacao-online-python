# Model da Entidade (`app/models/{entity}.py`)

Sempre herdar de `TimestampedModel`. Os campos `id`, `created_at` e `updated_at` são herdados automaticamente — **nunca** repeti-los no model.

Campos declarados com o modificador `unique` no `campos:` da invocação (ex: `sku: str unique`) recebem `unique=True, index=True` na coluna — o mesmo padrão já usado em `User.email` no scaffold.

```python
from sqlalchemy import String, Boolean, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import TimestampedModel

class {Entity}(TimestampedModel):
    __tablename__ = "{entities}"

    # campo comum:  {field}: Mapped[{type}] = mapped_column({SQLType})
    # campo unique: {field}: Mapped[{type}] = mapped_column({SQLType}, unique=True, index=True)
```

## Mapeamento de Tipos Python → SQLAlchemy

| Python     | SQLAlchemy Mapped                                           |
|------------|-------------------------------------------------------------|
| `str`      | `Mapped[str] = mapped_column(String(255))`                  |
| `int`      | `Mapped[int] = mapped_column(Integer)`                      |
| `float`    | `Mapped[float] = mapped_column(Float)`                      |
| `bool`     | `Mapped[bool] = mapped_column(Boolean)`                     |
| `date`     | `Mapped[date] = mapped_column(Date)`                        |
| `datetime` | `Mapped[datetime] = mapped_column(DateTime(timezone=True))` |
| `Decimal`  | `Mapped[Decimal] = mapped_column(Numeric(10, 2))`           |
| `Text`     | `Mapped[str] = mapped_column(Text)`                         |

Se o usuário fornecer um tipo fora desta tabela (ex.: `list`, `dict`, `any`), pergunte antes de assumir um mapeamento.
