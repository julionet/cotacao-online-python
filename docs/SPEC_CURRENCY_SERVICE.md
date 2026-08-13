# ESPECIFICAÇÃO TDD: Currency Service - list_activate Method

**Título:** Integração com Airtable - Implementação do método `list_activate`  
**Arquivo:** `currency_service.py`  
**Método:** `list_activate()`  
**Versão:** 1.0  
**Data:** 2026-01-15  

---

## 1. OBJETIVO

Implementar o método `list_activate()` em `currency_service.py` para:
- Consumir GET endpoint Airtable `/Currency`
- Filtrar registros onde `fields.Active == true`
- Mapear resposta Airtable para lista de `CurrencyResponse`
- Retornar instância de lista de `CurrencyResponse` ordenada conforme API

---

## 2. ESTRUTURA DE DADOS

### 2.1 Modelo de Entrada (Response Airtable)

```json
{
  "records": [
    {
      "id": "recFTu2BE9PnKgJ4u",
      "createdTime": "2026-08-12T23:14:52.000Z",
      "fields": {
        "Active": true,
        "Max": 6,
        "Origin": "BRL",
        "Destiny": "EUR",
        "Name": "BRL_EUR",
        "Exchange": ["recov2d7ZkAekb9AM"],
        "Min": 5.9
      }
    }
  ]
}
```

### 2.2 Modelo de Saída (CurrencyResponse)

```python
class CurrencyResponse(BaseModel):
    id: str                    # Origem: record.id (ex: "recFTu2BE9PnKgJ4u")
    name: str                  # Origem: fields.Name (ex: "BRL_EUR")
    code: str                  # Origem: fields.Origin (ex: "BRL")
    codein: str                # Origem: fields.Destiny (ex: "EUR")
    last_date: datetime        # Origem: createdTime (ex: "2026-08-12T23:14:52.000Z")

    model_config = {"from_attributes": True}
```

### 2.3 Mapeamento de Campos (Airtable → CurrencyResponse)

| CurrencyResponse | Airtable Record | Tipo | Exemplo |
|------------------|-----------------|------|---------|
| `id` | `records[].id` | string | "recFTu2BE9PnKgJ4u" |
| `name` | `records[].fields.Name` | string | "BRL_EUR" |
| `code` | `records[].fields.Origin` | string | "BRL" |
| `codein` | `records[].fields.Destiny` | string | "EUR" |
| `last_date` | `records[].createdTime` | datetime (ISO8601) | "2026-08-12T23:14:52.000Z" |

**Campos ignorados:**
- `fields.Active` (usado apenas para filtro)
- `fields.Max` (descartado)
- `fields.Min` (descartado)
- `fields.Exchange` (descartado)

---

## 3. CONFIGURAÇÃO .env

```bash
# Airtable Credentials
AIRTABLE_TOKEN=pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AIRTABLE_BASE_ID=appuYguoOyIkYfEK4
AIRTABLE_TABLE_CURRENCY=Currency

# Optional - Request Timeout
AIRTABLE_TIMEOUT=30
```

---

## 4. MÉTODO list_activate()

### 4.1 Assinatura

```python
async def list_activate(self) -> list[CurrencyResponse]:
    """
    Busca todas as moedas ativas (Active == true) do Airtable.
    
    Returns:
        list[CurrencyResponse]: Lista de moedas configuradas e ativas
        
    Raises:
        HTTPException: Se falhar ao conectar com Airtable (status 4xx/5xx)
        ValueError: Se resposta Airtable estiver malformada
    """
```

### 4.2 Lógica de Implementação

```
1. Carregar variáveis de ambiente:
   - AIRTABLE_TOKEN
   - AIRTABLE_BASE_ID
   - AIRTABLE_TABLE_CURRENCY

2. Construir URL:
   endpoint = "https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_CURRENCY}"
   
3. Fazer requisição HTTP (GET):
   - URL: endpoint construído
   - Header: Authorization: Bearer {AIRTABLE_TOKEN}
   - Header: Content-Type: application/json
   - Timeout: AIRTABLE_TIMEOUT (padrão 30s)
   
4. Validar resposta:
   - Status HTTP 200 OK?
   - Campo "records" existe?
   - "records" é uma lista?
   
5. Filtrar registros:
   - Para cada record em records:
     - Se fields.Active == true:
       - Extrair id, Name, Origin, Destiny, createdTime
     - Senão:
       - Descartar registro
       
6. Mapear para CurrencyResponse:
   - id = record["id"]
   - name = record["fields"]["Name"]
   - code = record["fields"]["Origin"]
   - codein = record["fields"]["Destiny"]
   - last_date = parseDateTime(record["createdTime"])
   
7. Retornar:
   - list[CurrencyResponse] (mesma ordem da API)
```

---

## 5. CASOS DE TESTE

### 5.1 Happy Path

#### TC-001: Requisição bem-sucedida com múltiplos registros ativos

**Given:** Airtable retorna 3 registros, todos com `Active == true`

**When:** `list_activate()` é chamado

**Then:**
- Status HTTP: 200
- Retorna lista com 3 `CurrencyResponse`
- Cada instância possui `id`, `name`, `code`, `codein`, `last_date` preenchidos
- Ordem mantém sequência da API
- Nenhuma exceção é lançada

**Expected Output:**
```python
[
    CurrencyResponse(
        id="recFTu2BE9PnKgJ4u",
        name="BRL_EUR",
        code="BRL",
        codein="EUR",
        last_date=datetime(2026, 8, 12, 23, 14, 52, tzinfo=timezone.utc)
    ),
    CurrencyResponse(
        id="rec2BE9PnKgJ4u2d7",
        name="BRL_USD",
        code="BRL",
        codein="USD",
        last_date=datetime(2026, 8, 12, 23, 15, 00, tzinfo=timezone.utc)
    ),
    CurrencyResponse(
        id="rec9PnKgJ4u2d7AMS",
        name="BRL_ARS",
        code="BRL",
        codein="ARS",
        last_date=datetime(2026, 8, 12, 23, 15, 10, tzinfo=timezone.utc)
    )
]
```

---

#### TC-002: Requisição com múltiplos registros, alguns inativos

**Given:** Airtable retorna 5 registros:
- 3 com `Active == true`
- 2 com `Active == false`

**When:** `list_activate()` é chamado

**Then:**
- Retorna lista com apenas 3 `CurrencyResponse` (somente ativos)
- Registros inativos são completamente descartados
- Nenhuma exceção é lançada

**Example Response:**
```json
{
  "records": [
    { "id": "rec1", "fields": { "Active": true, "Name": "BRL_USD", "Origin": "BRL", "Destiny": "USD" }, "createdTime": "2026-08-12T23:14:52.000Z" },
    { "id": "rec2", "fields": { "Active": false, "Name": "BRL_GBP", "Origin": "BRL", "Destiny": "GBP" }, "createdTime": "2026-08-12T23:14:52.000Z" },
    { "id": "rec3", "fields": { "Active": true, "Name": "BRL_EUR", "Origin": "BRL", "Destiny": "EUR" }, "createdTime": "2026-08-12T23:14:52.000Z" },
    { "id": "rec4", "fields": { "Active": false, "Name": "BRL_JPY", "Origin": "BRL", "Destiny": "JPY" }, "createdTime": "2026-08-12T23:14:52.000Z" },
    { "id": "rec5", "fields": { "Active": true, "Name": "BRL_ARS", "Origin": "BRL", "Destiny": "ARS" }, "createdTime": "2026-08-12T23:14:52.000Z" }
  ]
}
```

**Result:** 3 instâncias de `CurrencyResponse` (rec1, rec3, rec5)

---

#### TC-003: Nenhum registro ativo

**Given:** Airtable retorna 2 registros, todos com `Active == false`

**When:** `list_activate()` é chamado

**Then:**
- Retorna lista vazia `[]`
- Tipo é `list[CurrencyResponse]` (lista vazia, não None)
- Nenhuma exceção é lançada

---

### 5.2 Edge Cases

#### TC-004: Tabela vazia (nenhum registro)

**Given:** Airtable retorna `{ "records": [] }`

**When:** `list_activate()` é chamado

**Then:**
- Retorna lista vazia `[]`
- Nenhuma exceção é lançada

---

#### TC-005: Campo createdTime em diferentes formatos ISO8601

**Given:** Airtable retorna registros com timestamps válidos ISO8601:
- "2026-08-12T23:14:52.000Z"
- "2026-08-12T23:14:52Z"
- "2026-08-12T23:14:52+00:00"

**When:** `list_activate()` é chamado

**Then:**
- Todos são parseados corretamente para `datetime`
- `last_date` em cada instância está correto
- Timezone é preservado (UTC)

---

#### TC-006: Strings vazias em campos obrigatórios

**Given:** Airtable retorna registro com:
```json
{
  "id": "recXYZ",
  "createdTime": "2026-08-12T23:14:52.000Z",
  "fields": {
    "Active": true,
    "Name": "",
    "Origin": "",
    "Destiny": ""
  }
}
```

**When:** `list_activate()` é chamado

**Then:**
- Instância de `CurrencyResponse` é criada com strings vazias
- Não lança exceção (validação é de responsabilidade do model)
- `id` e `last_date` estão presentes

---

### 5.3 Erro Scenarios

#### TC-007: Falha na autenticação (401 Unauthorized)

**Given:** AIRTABLE_TOKEN inválido ou expirado

**When:** `list_activate()` é chamado

**Then:**
- Lança `HTTPException` com status 401
- Mensagem: "Unauthorized: Invalid Airtable token"
- Log level: WARNING

---

#### TC-008: Tabela não encontrada (404 Not Found)

**Given:** AIRTABLE_BASE_ID ou AIRTABLE_TABLE_CURRENCY incorretos

**When:** `list_activate()` é chamado

**Then:**
- Lança `HTTPException` com status 404
- Mensagem: "Not Found: Currency table not accessible"
- Log level: ERROR

---

#### TC-009: Timeout na conexão

**Given:** Airtable API não responde em AIRTABLE_TIMEOUT segundos

**When:** `list_activate()` é chamado

**Then:**
- Lanza `HTTPException` com status 504 (Gateway Timeout)
- Mensagem: "Request timeout: Airtable API not responding"
- Log level: ERROR

---

#### TC-010: Resposta Airtable malformada (campo "records" ausente)

**Given:** Airtable retorna JSON sem campo "records":
```json
{
  "error": { "type": "INVALID_REQUEST_UNKNOWN" }
}
```

**When:** `list_activate()` é chamado

**Then:**
- Lança `ValueError` ou `KeyError`
- Mensagem: "Invalid Airtable response: 'records' field not found"
- Log level: ERROR

---

#### TC-011: Resposta Airtable com campo "records" não sendo lista

**Given:** Airtable retorna `{ "records": "string" }` (inválido)

**When:** `list_activate()` é chamado

**Then:**
- Lanza `ValueError`
- Mensagem: "Invalid Airtable response: 'records' must be a list"
- Log level: ERROR

---

#### TC-012: Variável de ambiente AIRTABLE_TOKEN não configurada

**Given:** .env não possui AIRTABLE_TOKEN

**When:** `list_activate()` é chamado

**Then:**
- Lanza `ValueError` ou `KeyError`
- Mensagem: "Missing environment variable: AIRTABLE_TOKEN"
- Log level: CRITICAL
- Aplicação falha ao iniciar (ou no primeiro uso)

---

## 6. TRATAMENTO DE ERROS

### 6.1 Hierarquia de Exceções

```
HTTPException (FastAPI)
├── 401 Unauthorized (AIRTABLE_TOKEN inválido)
├── 404 Not Found (tabela/base não existem)
├── 500 Internal Server Error (erro no Airtable)
└── 504 Gateway Timeout (timeout na requisição)

ValueError (Python Built-in)
├── Missing environment variable
└── Malformed Airtable response

KeyError (Python Built-in)
├── Campo "records" ausente
└── Campo obrigatório em fields ausente
```

### 6.2 Logging

**Nivel INFO:**
- Início da requisição: `"Fetching active currencies from Airtable"`
- Sucesso: `"Successfully fetched {count} active currencies"`

**Nivel WARNING:**
- Nenhum registro ativo: `"No active currencies found in Airtable"`

**Nivel ERROR:**
- Falha HTTP 4xx/5xx: `"Airtable API error: {status_code} {message}"`
- Timeout: `"Request timeout while connecting to Airtable"`
- Resposta malformada: `"Malformed Airtable response: {details}"`

**Nivel CRITICAL:**
- Variável de ambiente ausente: `"Missing critical config: {var_name}"`

---

## 7. CRITÉRIOS DE ACEITAÇÃO

### 7.1 Funcionais

- ✅ Método retorna `list[CurrencyResponse]` (tipo exato)
- ✅ Apenas registros com `fields.Active == true` são inclusos
- ✅ Mapeamento de campos segue especificação (seção 2.3)
- ✅ `last_date` é parseado como `datetime` com timezone UTC
- ✅ Ordem de registros mantém sequência da API Airtable
- ✅ Lista vazia quando nenhum registro ativo
- ✅ Lista vazia quando nenhum registro existe
- ✅ Campos `Max`, `Min`, `Exchange` são ignorados

### 7.2 Não-Funcionais

- ✅ Timeout máximo: 30 segundos (configurável via .env)
- ✅ Requisição HTTP usa header `Authorization: Bearer {token}`
- ✅ Content-Type: application/json
- ✅ Logging implementado (INFO, WARNING, ERROR, CRITICAL)
- ✅ Sem hardcoding de credenciais (uso obrigatório de .env)
- ✅ Método é async (se não for, será síncrono)

### 7.3 Exceções

- ✅ HTTPException para erros 4xx/5xx
- ✅ ValueError para dados malformados
- ✅ KeyError/AttributeError tratados ou transformados em ValueError
- ✅ Mensagem de erro descritiva e orientada ao desenvolvedor
- ✅ Nenhuma exceção é silenciada (re-raise ou log + raise)

---

## 8. EXEMPLO DE IMPLEMENTAÇÃO

### 8.1 Imports Necessários

```python
import os
from datetime import datetime
from typing import List
from pydantic import BaseModel
import httpx
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)
```

### 8.2 Estrutura Base

```python
class CurrencyResponse(BaseModel):
    id: str
    name: str
    code: str
    codein: str
    last_date: datetime

    model_config = {"from_attributes": True}


class CurrencyService:
    
    async def list_activate(self) -> list[CurrencyResponse]:
        """
        Busca todas as moedas ativas (Active == true) do Airtable.
        
        Returns:
            list[CurrencyResponse]: Lista de moedas configuradas e ativas
            
        Raises:
            HTTPException: Se falhar ao conectar com Airtable
            ValueError: Se resposta estiver malformada
        """
        # TODO: Implementação
        pass
```

### 8.3 Pseudo-código da Implementação

```python
async def list_activate(self) -> list[CurrencyResponse]:
    # 1. Validar variáveis de ambiente
    try:
        airtable_token = os.getenv("AIRTABLE_TOKEN")
        airtable_base_id = os.getenv("AIRTABLE_BASE_ID")
        airtable_table = os.getenv("AIRTABLE_TABLE_CURRENCY", "Currency")
        airtable_timeout = int(os.getenv("AIRTABLE_TIMEOUT", "30"))
        
        if not airtable_token or not airtable_base_id:
            raise ValueError("Missing environment variables: AIRTABLE_TOKEN and AIRTABLE_BASE_ID")
    except ValueError as e:
        logger.critical(f"Configuration error: {str(e)}")
        raise
    
    # 2. Construir URL e headers
    url = f"https://api.airtable.com/v0/{airtable_base_id}/{airtable_table}"
    headers = {
        "Authorization": f"Bearer {airtable_token}",
        "Content-Type": "application/json"
    }
    
    # 3. Fazer requisição HTTP
    logger.info(f"Fetching active currencies from Airtable: {url}")
    
    try:
        async with httpx.AsyncClient(timeout=airtable_timeout) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()  # Lança HTTPException para 4xx/5xx
    except httpx.HTTPStatusError as e:
        error_msg = f"Airtable API error: {e.response.status_code} {e.response.text}"
        logger.error(error_msg)
        raise HTTPException(status_code=e.response.status_code, detail=error_msg)
    except httpx.TimeoutException:
        error_msg = "Request timeout while connecting to Airtable"
        logger.error(error_msg)
        raise HTTPException(status_code=504, detail=error_msg)
    except httpx.RequestError as e:
        error_msg = f"Request error: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
    
    # 4. Parsear resposta JSON
    try:
        data = response.json()
    except ValueError:
        error_msg = "Malformed Airtable response: Invalid JSON"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # 5. Validar estrutura da resposta
    if "records" not in data:
        error_msg = "Invalid Airtable response: 'records' field not found"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    records = data.get("records")
    if not isinstance(records, list):
        error_msg = "Invalid Airtable response: 'records' must be a list"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # 6. Filtrar e mapear registros
    currencies: list[CurrencyResponse] = []
    
    for record in records:
        try:
            # Verificar se registro está ativo
            fields = record.get("fields", {})
            if not fields.get("Active", False):
                continue
            
            # Parsear createdTime
            created_time_str = record.get("createdTime")
            if not created_time_str:
                logger.warning(f"Record {record.get('id')} missing createdTime, skipping")
                continue
            
            last_date = datetime.fromisoformat(created_time_str.replace('Z', '+00:00'))
            
            # Criar instância CurrencyResponse
            currency = CurrencyResponse(
                id=record.get("id"),
                name=fields.get("Name"),
                code=fields.get("Origin"),
                codein=fields.get("Destiny"),
                last_date=last_date
            )
            currencies.append(currency)
            
        except (KeyError, ValueError, AttributeError) as e:
            logger.error(f"Error mapping record {record.get('id')}: {str(e)}")
            continue  # Pula registro inválido, continua com próximo
    
    # 7. Retornar resultado
    if not currencies:
        logger.warning("No active currencies found in Airtable")
    else:
        logger.info(f"Successfully fetched {len(currencies)} active currencies")
    
    return currencies
```
 
---

## 10. CHECKLIST DE IMPLEMENTAÇÃO

- [ ] Método assinado como `async def list_activate(self) -> list[CurrencyResponse]`
- [ ] Carregar variáveis de ambiente (AIRTABLE_TOKEN, AIRTABLE_BASE_ID, AIRTABLE_TABLE_CURRENCY, AIRTABLE_TIMEOUT)
- [ ] Validar variáveis de ambiente não vazias
- [ ] Construir URL endpoint corretamente
- [ ] Fazer requisição GET com Bearer token
- [ ] Tratar erros HTTP (401, 404, 500, 504)
- [ ] Parsear JSON response
- [ ] Validar campo "records" existe e é lista
- [ ] Iterar sobre records
- [ ] Filtrar por `fields.Active == true`
- [ ] Mapear campos conforme seção 2.3
- [ ] Parsear `createdTime` para datetime com timezone UTC
- [ ] Criar instâncias de `CurrencyResponse`
- [ ] Retornar `list[CurrencyResponse]`
- [ ] Implementar logging (INFO, WARNING, ERROR, CRITICAL)
- [ ] Sem exceções silenciadas
- [ ] Tratamento de edge cases (strings vazias, timestamps diferentes)

---

## 11. ARQUIVO .env (Exemplo)

```bash
# Airtable Configuration
AIRTABLE_TOKEN=pat_abc123def456ghi789jklmnopqrstuv
AIRTABLE_BASE_ID=appuYguoOyIkYfEK4
AIRTABLE_TABLE_CURRENCY=Currency
AIRTABLE_TIMEOUT=30

# Logging
LOG_LEVEL=INFO
```

---

**Status:** ✅ Especificação Completa - Pronto para Implementação

**Responsável:** Jose Julio 
