# ATUALIZAÇÃO: Currency Service - Adicionar Atributo Exchange

**Arquivo:** `currency_service.py`  
**Método:** `list_activate()`  
**Alteração:** Incluir campo `exchange` em CurrencyResponse  
**Versão:** 1.1  

---

## MUDANÇA REQUERIDA

### Antes (Versão 1.0)

```python
class CurrencyResponse(BaseModel):
    id: str
    name: str
    code: str
    codein: str
    last_date: datetime

    model_config = {"from_attributes": True}
```

### Depois (Versão 1.1)

```python
class CurrencyResponse(BaseModel):
    id: str                          # Airtable record ID (ex: "recFTu2BE9PnKgJ4u")
    name: str                        # Nome do par (ex: "BRL_EUR")
    code: str                        # Moeda origem (ex: "BRL")
    codein: str                      # Moeda destino (ex: "EUR")
    last_date: datetime              # Data criação (createdTime)
    exchange: list[str] | None       # IDs do Exchange relacionado (novo campo)

    model_config = {"from_attributes": True}
```

---

## MAPEAMENTO DO NOVO CAMPO

| Campo | Origem | Tipo | Exemplo | Comportamento |
|-------|--------|------|---------|---------------|
| `exchange` | `record.fields.Exchange` | `list[str] \| None` | `["recov2d7ZkAekb9AM"]` ou `[]` ou `None` | Array de record IDs do Airtable ou vazio |

---

## IMPLEMENTAÇÃO

### Mudança no Método list_activate()

**Adicionar mapeamento:**

```python
# Antes:
currency = CurrencyResponse(
    id=record.get("id"),
    name=fields.get("Name"),
    code=fields.get("Origin"),
    codein=fields.get("Destiny"),
    last_date=last_date
)

# Depois:
currency = CurrencyResponse(
    id=record.get("id"),
    name=fields.get("Name"),
    code=fields.get("Origin"),
    codein=fields.get("Destiny"),
    last_date=last_date,
    exchange=fields.get("Exchange")  # Novo campo
)
```

---

## VALIDAÇÃO

### Possíveis Valores

1. **Array com IDs (Exchange existe):**
   ```python
   exchange = ["recov2d7ZkAekb9AM"]
   # Resultado: Exchange existente, deve fazer PUT
   ```

2. **Array vazio (Exchange não existe):**
   ```python
   exchange = []
   # Resultado: Exchange não existe, deve fazer POST
   ```

3. **None (Campo não retornado):**
   ```python
   exchange = None
   # Resultado: Exchange não existe, deve fazer POST
   ```

---

## CHECKLIST

- [ ] Adicionar `exchange: list[str] | None` ao CurrencyResponse
- [ ] Atualizar método list_activate() para mapear `fields.Exchange`
- [ ] Testar se resposta Airtable contém o campo
- [ ] Validar se array vazio é retornado corretamente
- [ ] Validar se None é retornado corretamente
- [ ] Atualizar testes unitários (TC-001, TC-002, etc)
- [ ] Documentação atualizada

---

**Status:** ✅ Pronto para implementar

**Impacto:** Mínimo - apenas adição de novo campo sem quebra de compatibilidade
