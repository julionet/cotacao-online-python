# ESPECIFICAÇÃO SDD: Exchange Sync Service

**Título:** Sincronização de Cotações de Moedas  
**Arquivo:** `exchange_service.py` (novo)  
**Versão:** 1.0  
**Data:** 2026-08-13  
**Formato:** Specification Driven Development (SDD)

---

## 1. OBJETIVO

Implementar serviço de sincronização de cotações que:
- Obtém lista de moedas ativas via `currency_service.list_activate()`
- Busca cotações em tempo real na AwesomeAPI
- Atualiza ou cria registros na tabela Exchange do Airtable
- Calcula variação em relação à cotação anterior

---

## 2. ESCOPO

### 2.1 Componentes Envolvidos

1. **Currency Service** (existente)
   - Método: `currency_service.list_activate()`
   - Retorna: `list[CurrencyResponse]`
   - CurrencyResponse contém: `id`, `name`, `code`, `codein`, `last_date`, `exchange`

2. **AwesomeAPI** (integração nova)
   - Endpoint: `https://economia.awesomeapi.com.br/json/last/{code}-{codein}`
   - Método: GET
   - Autenticação: Nenhuma (API pública)
   - Timeout: 15 segundos (configurável)

3. **Airtable Exchange** (integração nova)
   - Operações: GET (verificar existência), PUT (atualizar), POST (criar)
   - Tabela: Exchange
   - Base ID: appuYguoOyIkYfEK4

---

## 3. FLUXO PRINCIPAL

```
1. Chamar currency_service.list_activate()
   ↓
2. Iterar sobre cada CurrencyResponse na lista
   ↓
   ├─→ 3. Construir URL AwesomeAPI: {code}-{codein}
   │    ↓
   │    4. Chamar GET AwesomeAPI
   │    ↓
   │    5. Extrair dados da resposta (varBid, pctChange, create_date, bid, ask)
   │    ↓
   │    6. Validar dados recebidos
   │    ↓
   │    7. Verificar se currency.exchange não é None
   │    ↓
   │    ├─→ SIM (tem ID): 8a. Fazer PUT no Airtable (atualizar Exchange existente)
   │    │    ↓
   │    │    9. Retornar resposta PUT
   │    │
   │    └─→ NÃO (None): 8b. Fazer POST no Airtable (criar novo Exchange)
   │         ↓
   │         9. Retornar resposta POST
   │
   10. Continuar com próxima moeda
   ↓
11. Retornar resultado da sincronização
```

---

## 4. MODELOS DE DADOS

### 4.1 CurrencyResponse (do currency_service)

```python
class CurrencyResponse(BaseModel):
    id: str                          # Airtable record ID (ex: "recFTu2BE9PnKgJ4u")
    name: str                        # Nome do par (ex: "BRL_EUR")
    code: str                        # Moeda origem (ex: "BRL")
    codein: str                      # Moeda destino (ex: "EUR")
    last_date: datetime              # Data criação
    exchange: str | None             # ID do Exchange no Airtable (primeiro item do array, ex: "recov2d7ZkAekb9AM" ou None)
    
    model_config = {"from_attributes": True}
```

### 4.2 AwesomeAPI Response

**URL:** `https://economia.awesomeapi.com.br/json/last/USD-BRL`

**Formato JSON Recebido:**
```json
{
  "USDBRL": {
    "code": "USD",
    "codein": "BRL",
    "name": "Dólar Americano/Real Brasileiro",
    "high": "5.1919",
    "low": "5.13525",
    "varBid": "0.0331",
    "pctChange": "0.641809",
    "bid": "5.1904",
    "ask": "5.1914",
    "timestamp": "1786570192",
    "create_date": "2026-08-12 18:29:52"
  }
}
```

**Campos Utilizados:**
- `bid` (string) → Airtable `Bid` (number)
- `ask` (string) → Airtable `Ask` (number)
- `varBid` (string) → Airtable `Variation` (number)
- `pctChange` (string) → Airtable `Percent` (number)
- `create_date` (string) → Airtable `Timestamp` (string, mesmo formato)

**Campos Ignorados:**
- `code`, `codein`, `name`, `high`, `low`, `timestamp`

---

### 4.3 Airtable Exchange - POST (Criar)

**Endpoint:** `https://api.airtable.com/v0/appuYguoOyIkYfEK4/Exchange`

**Método:** POST

**Headers:**
```
Authorization: Bearer {AIRTABLE_TOKEN}
Content-Type: application/json
```

**Body (Request):**
```json
{
  "fields": {
    "Guid": "7f9efcf4-66f7-440d-b213-58e72de5c8a3",
    "Bid": 5.1904,
    "Ask": 5.1914,
    "Variation": 0.0331,
    "Percent": 0.641809,
    "Timestamp": "2026-08-12 18:29:52",
    "Currency": ["recFTu2BE9PnKgJ4u"]
  }
}
```

**Mapeamento:**
- `Guid`: UUID v4 gerado pelo backend
- `Bid`: AwesomeAPI.bid (converter string para float)
- `Ask`: AwesomeAPI.ask (converter string para float)
- `Variation`: AwesomeAPI.varBid (converter string para float)
- `Percent`: AwesomeAPI.pctChange (converter string para float)
- `Timestamp`: AwesomeAPI.create_date (string, mesmo formato)
- `Currency`: array com `currency.id` (ex: ["recFTu2BE9PnKgJ4u"])

**Response (Success - 200):**
```json
{
  "id": "recY2A7YnpsLTCsXO",
  "createdTime": "2026-08-13T01:48:25.000Z",
  "fields": {
    "Guid": "7f9efcf4-66f7-440d-b213-58e72de5c8a3",
    "Bid": 5.1904,
    "Ask": 5.1914,
    "Variation": 0.0331,
    "Percent": 0.641809,
    "Timestamp": "2026-08-12 18:29:52",
    "Currency": ["recFTu2BE9PnKgJ4u"]
  }
}
```

---

### 4.4 Airtable Exchange - PUT (Atualizar)

**Endpoint:** `https://api.airtable.com/v0/appuYguoOyIkYfEK4/Exchange/{recordId}`

**Método:** PUT

**Headers:**
```
Authorization: Bearer {AIRTABLE_TOKEN}
Content-Type: application/json
```

**Body (Request):**
```json
{
  "fields": {
    "Bid": 5.1904,
    "Ask": 5.1914,
    "Variation": 0.0331,
    "Percent": 0.641809,
    "Timestamp": "2026-08-12 18:29:52"
  }
}
```

**Mapeamento (igual ao POST, exceto):**
- `Guid`: NÃO incluir (campo existente não é atualizado)
- `Currency`: NÃO incluir (FK não é atualizado)
- Demais campos: idem ao POST

**Response (Success - 200):**
```json
{
  "id": "recY2A7YnpsLTCsXO",
  "createdTime": "2026-08-12T23:14:52.000Z",
  "fields": {
    "Guid": "7f9efcf4-66f7-440d-b213-58e72de5c8a3",
    "Bid": 5.1904,
    "Ask": 5.1914,
    "Variation": 0.0331,
    "Percent": 0.641809,
    "Timestamp": "2026-08-12 18:29:52",
    "Currency": ["recFTu2BE9PnKgJ4u"]
  }
}
```

---

## 5. CONFIGURAÇÃO .env

```bash
# Airtable Credentials
AIRTABLE_TOKEN=pat_xxxxx
AIRTABLE_BASE_ID=appuYguoOyIkYfEK4
AIRTABLE_TABLE_EXCHANGE=Exchange

# AwesomeAPI Configuration
EXCHANGE_API_URL=https://economia.awesomeapi.com.br/json/last
EXCHANGE_API_TIMEOUT=15

# Logging
LOG_LEVEL=INFO
```

---

## 6. MÉTODOS DO EXCHANGE SERVICE

### 6.1 sync_all()

**Assinatura:**
```python
async def sync_all(self) -> dict:
    """
    Sincroniza todas as moedas ativas com suas cotações.
    
    Fluxo:
    1. Busca moedas ativas via currency_service.list_activate()
    2. Para cada moeda: busca cotação na AwesomeAPI
    3. Para cada cotação: atualiza ou cria registro em Exchange (Airtable)
    
    Returns:
        dict com estrutura:
        {
            "success": bool,
            "total_currencies": int,
            "updated": int,
            "created": int,
            "failed": int,
            "errors": list[dict],
            "timestamp": str
        }
    
    Raises:
        HTTPException: Erro ao conectar com currency_service ou Airtable
        ValueError: Dados malformados
    """
```

**Retorno (Exemplo - Success):**
```json
{
    "success": true,
    "total_currencies": 3,
    "updated": 2,
    "created": 1,
    "failed": 0,
    "errors": [],
    "timestamp": "2026-08-13T01:48:25.123456Z"
}
```

**Retorno (Exemplo - Com Erros):**
```json
{
    "success": false,
    "total_currencies": 3,
    "updated": 1,
    "created": 1,
    "failed": 1,
    "errors": [
        {
            "currency": "BRL_ARS",
            "error_type": "APIError",
            "message": "AwesomeAPI returned 500",
            "timestamp": "2026-08-13T01:48:25.123456Z"
        }
    ],
    "timestamp": "2026-08-13T01:48:26.789012Z"
}
```

---

### 6.2 _fetch_awesome_api()

**Assinatura (Private):**
```python
async def _fetch_awesome_api(self, code: str, codein: str) -> dict:
    """
    Busca cotação na AwesomeAPI para um par específico.
    
    Args:
        code (str): Moeda origem (ex: "USD")
        codein (str): Moeda destino (ex: "BRL")
    
    Returns:
        dict com campos: bid, ask, varBid, pctChange, create_date
    
    Raises:
        HTTPException: Erro na requisição
        ValueError: Resposta malformada
    """
```

**Lógica Interna:**
1. Construir URL: `{EXCHANGE_API_URL}/{code}-{codein}`
2. Fazer GET com timeout EXCHANGE_API_TIMEOUT
3. Parsear JSON response
4. Extrair chave principal (ex: "USDBRL")
5. Validar campos obrigatórios (bid, ask, varBid, pctChange, create_date)
6. Converter strings numéricas para float
7. Retornar dict com dados extraídos

---

### 6.3 _sync_exchange()

**Assinatura (Private):**
```python
async def _sync_exchange(
    self, 
    currency: CurrencyResponse, 
    quote: dict
) -> dict:
    """
    Sincroniza uma cotação no Airtable (POST ou PUT).
    
    Args:
        currency (CurrencyResponse): Moeda com possível Exchange relacionado
        quote (dict): Dados da cotação (bid, ask, varBid, pctChange, create_date)
    
    Returns:
        dict com estrutura:
        {
            "action": "created" | "updated",
            "record_id": str,
            "guid": str,
            "success": bool
        }
    
    Raises:
        HTTPException: Erro na requisição Airtable
        ValueError: Dados inválidos
    """
```

**Lógica Interna:**
1. Verificar se `currency.exchange` é None
2. Se NÃO é None (tem ID de string):
   - Fazer PUT no ID do exchange
   - Atualizar campos: Bid, Ask, Variation, Percent, Timestamp
3. Se é None (Exchange não existe):
   - Gerar UUID v4 (Guid)
   - Fazer POST com todos os campos (incluindo Guid e Currency como ["recId"])
4. Retornar resultado com action ("created"/"updated")

---

## 7. DETALHES DE IMPLEMENTAÇÃO

### 7.1 Geração de UUID

```python
import uuid

guid = str(uuid.uuid4())  # Exemplo: "7f9efcf4-66f7-440d-b213-58e72de5c8a3"
```

---

### 7.2 Conversão de Tipos

**AwesomeAPI retorna strings, converter para números:**
```python
bid = float(quote["bid"])       # "5.1904" → 5.1904
ask = float(quote["ask"])       # "5.1914" → 5.1914
variation = float(quote["varBid"])    # "0.0331" → 0.0331
percent = float(quote["pctChange"])   # "0.641809" → 0.641809
timestamp = quote["create_date"]      # "2026-08-12 18:29:52" → string (sem conversão)
```

---

### 7.3 Construção de URL AwesomeAPI

```python
code = "USD"      # currency.code
codein = "BRL"    # currency.codein

url = f"{EXCHANGE_API_URL}/{code.lower()}-{codein.lower()}"
# Resultado: "https://economia.awesomeapi.com.br/json/last/usd-brl"
```

---

### 7.4 Extração de Dados da Resposta AwesomeAPI

**A resposta tem a chave dinâmica baseada no par:**
```python
# Response recebido:
response = {
    "USDBRL": {
        "bid": "5.1904",
        "ask": "5.1914",
        ...
    }
}

# Extrair dados:
key = f"{code.upper()}{codein.upper()}"  # "USDBRL"
data = response[key]
quote = {
    "bid": float(data["bid"]),
    "ask": float(data["ask"]),
    "varBid": float(data["varBid"]),
    "pctChange": float(data["pctChange"]),
    "create_date": data["create_date"]
}
```

---

### 7.5 Identificação de Exchange Existente

```python
if currency.exchange:
    # Exchange existe (currency.exchange contém string com ID)
    exchange_id = currency.exchange
    # Fazer PUT em: https://api.airtable.com/v0/{BASE_ID}/Exchange/{exchange_id}
else:
    # Exchange não existe (currency.exchange é None)
    # Fazer POST em: https://api.airtable.com/v0/{BASE_ID}/Exchange
```

---

### 7.6 Construção do Body para Airtable

**Para POST (criar):**
```python
body = {
    "fields": {
        "Guid": str(uuid.uuid4()),
        "Bid": bid,
        "Ask": ask,
        "Variation": variation,
        "Percent": percent,
        "Timestamp": timestamp,
        "Currency": [currency.id]
    }
}
```

**Para PUT (atualizar):**
```python
body = {
    "fields": {
        "Bid": bid,
        "Ask": ask,
        "Variation": variation,
        "Percent": percent,
        "Timestamp": timestamp
    }
}
```

---

## 8. TRATAMENTO DE ERROS

### 8.1 Categorias de Erro

| Erro | Status | Ação |
|------|--------|------|
| AwesomeAPI 4xx/5xx | HTTPException | Log ERROR, adicionar à lista de failed |
| AwesomeAPI Timeout | HTTPException 504 | Log ERROR, adicionar à lista de failed |
| AwesomeAPI resposta malformada | ValueError | Log ERROR, adicionar à lista de failed |
| Airtable 4xx/5xx | HTTPException | Log ERROR, adicionar à lista de failed |
| Airtable Timeout | HTTPException 504 | Log ERROR, adicionar à lista de failed |
| Currency Service indisponível | HTTPException | Log CRITICAL, abortar sincronização |
| Variável .env ausente | ValueError | Log CRITICAL, abortar sincronização |

### 8.2 Estratégia de Continuidade

- Se um currency falhar, continuar com o próximo
- Registrar erro detalhado (currency, tipo erro, mensagem)
- Retornar resumo com sucessos e falhas
- NÃO abortar sincronização por falha em currency individual

---

## 9. LOGGING

**Nivel INFO:**
- Início de sincronização
- Moedas encontradas
- Sucesso de POST/PUT individual

**Nivel WARNING:**
- Nenhuma moeda ativa encontrada
- Currency sem exchange relacionado (criando novo)

**Nivel ERROR:**
- Falha em AwesomeAPI (4xx/5xx)
- Falha em Airtable (4xx/5xx)
- Dados malformados
- Timeout

**Nivel CRITICAL:**
- Currency Service indisponível
- Variáveis de ambiente ausentes

---

## 10. REQUISITOS NÃO-FUNCIONAIS

| Requisito | Especificação |
|-----------|---------------|
| **Timeout** | 15s por requisição (AwesomeAPI), 30s total (Airtable) |
| **Retry** | Até 3 tentativas por currency com backoff exponencial (1s, 2s, 4s) |
| **Concorrência** | Requisições paralelas para múltiplos currencies (asyncio) |
| **Atomicidade** | Cada currency é independente (falha isolada) |
| **Idempotência** | PUT é idempotente; POST pode gerar duplicata se falhar |
| **Performance** | Sincronizar até 100 currencies em < 5 minutos |

---

## 11. DEPENDÊNCIAS E IMPORTS

```python
import os
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional
import httpx
from fastapi import HTTPException
import asyncio

from .currency_service import CurrencyService, CurrencyResponse
from core.config import settings

logger = logging.getLogger(__name__)
```

---

## 12. CLASSE EXCHANGE SERVICE

**Estrutura Base:**
```python
class ExchangeService:
    """Serviço de sincronização de cotações com AwesomeAPI e Airtable."""
    
    def __init__(self):
        self.currency_service = CurrencyService()
        self.airtable_token = os.getenv("AIRTABLE_TOKEN")
        self.airtable_base_id = os.getenv("AIRTABLE_BASE_ID")
        self.airtable_table = os.getenv("AIRTABLE_TABLE_EXCHANGE", "Exchange")
        self.exchange_api_url = os.getenv("EXCHANGE_API_URL")
        self.exchange_api_timeout = int(os.getenv("EXCHANGE_API_TIMEOUT", "15"))
    
    async def sync_all(self) -> dict:
        """Implementar conforme seção 6.1"""
        pass
    
    async def _fetch_awesome_api(self, code: str, codein: str) -> dict:
        """Implementar conforme seção 6.2"""
        pass
    
    async def _sync_exchange(
        self, 
        currency: CurrencyResponse, 
        quote: dict
    ) -> dict:
        """Implementar conforme seção 6.3"""
        pass
```

---

## 13. FLUXO DETALHADO DE EXECUÇÃO

### 13.1 Sincronização Completa (sync_all)

```
1. INICIALIZAÇÃO
   ├─ Log: "Starting currency sync..."
   ├─ Inicializar contadores: total=0, updated=0, created=0, failed=0
   └─ Inicializar lista de erros: errors=[]

2. BUSCAR MOEDAS ATIVAS
   ├─ Chamar currency_service.list_activate()
   ├─ Capturar resultado ou exceção
   └─ Se falhar: Log CRITICAL, retornar erro imediato

3. VALIDAR RESULTADO
   ├─ Se lista vazia: Log WARNING, retornar sucesso com 0 currencies
   └─ Caso contrário: total = len(currencies)

4. ITERAR SOBRE CURRENCIES
   ├─ Para cada currency na lista:
   │
   ├─ 4.1 LOG: "Processing {currency.name}..."
   │
   ├─ 4.2 BUSCAR COTAÇÃO
   │   ├─ Chamar _fetch_awesome_api(currency.code, currency.codein)
   │   ├─ Tratamento de erro:
   │   │  └─ Registrar erro, incrementar failed, continuar
   │   └─ Se sucesso: avançar
   │
   ├─ 4.3 SINCRONIZAR EXCHANGE
   │   ├─ Chamar _sync_exchange(currency, quote)
   │   ├─ Tratamento de erro:
   │   │  └─ Registrar erro, incrementar failed, continuar
   │   └─ Se sucesso:
   │       ├─ Se action == "created": incrementar created
   │       └─ Se action == "updated": incrementar updated
   │
   └─ Continuar para próxima currency

5. PREPARAR RESPOSTA
   ├─ success = (failed == 0)
   ├─ timestamp = datetime.now(timezone.utc).isoformat()
   └─ Retornar dict conforme seção 6.1

6. LOG FINAL
   ├─ Log INFO: "Sync completed: {updated} updated, {created} created, {failed} failed"
   └─ Se failed > 0: Log ERROR com detalhes dos erros
```

---

## 14. CASOS DE USO

### 14.1 Sincronização Normal (Todos Sucessos)

```
Input:
- 3 currencies ativas (BRL_USD, BRL_EUR, BRL_ARS)
- Todos com exchange relacionado (update scenario)

Output:
{
    "success": true,
    "total_currencies": 3,
    "updated": 3,
    "created": 0,
    "failed": 0,
    "errors": [],
    "timestamp": "2026-08-13T01:48:25.123456Z"
}
```

### 14.2 Sincronização com Criação de Novo Exchange

```
Input:
- 2 currencies ativas
  - BRL_USD: com exchange relacionado (update)
  - BRL_EUR: sem exchange (create)

Output:
{
    "success": true,
    "total_currencies": 2,
    "updated": 1,
    "created": 1,
    "failed": 0,
    "errors": [],
    "timestamp": "2026-08-13T01:48:25.123456Z"
}
```

### 14.3 Sincronização com Falhas Parciais

```
Input:
- 3 currencies
  - BRL_USD: sucesso
  - BRL_EUR: falha na AwesomeAPI (500)
  - BRL_ARS: sucesso

Output:
{
    "success": false,
    "total_currencies": 3,
    "updated": 2,
    "created": 0,
    "failed": 1,
    "errors": [
        {
            "currency": "BRL_EUR",
            "error_type": "HTTPStatusError",
            "message": "AwesomeAPI returned 500 Internal Server Error",
            "timestamp": "2026-08-13T01:48:25.234567Z"
        }
    ],
    "timestamp": "2026-08-13T01:48:26.789012Z"
}
```

---

## 15. INTEGRAÇÃO COM SCHEDULER

**Exemplo de agendamento (APScheduler):**
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

async def scheduled_sync():
    service = ExchangeService()
    result = await service.sync_all()
    logger.info(f"Scheduled sync result: {result}")

scheduler.add_job(
    scheduled_sync,
    "interval",
    minutes=15,
    id="exchange_sync"
)
scheduler.start()
```

---

## 16. CHECKLIST DE IMPLEMENTAÇÃO

- [ ] Classe ExchangeService criada
- [ ] Método sync_all() implementado
- [ ] Método _fetch_awesome_api() implementado
- [ ] Método _sync_exchange() implementado
- [ ] Carregamento .env para todas as variáveis
- [ ] Validação de variáveis de ambiente
- [ ] Logging implementado (INFO, WARNING, ERROR, CRITICAL)
- [ ] Tratamento de exceções HTTPException
- [ ] Tratamento de exceções ValueError
- [ ] Tratamento de timeout (15s AwesomeAPI, 30s Airtable)
- [ ] Geração de UUID v4
- [ ] Conversão de tipos (string → float)
- [ ] Construção correta de URLs
- [ ] Headers HTTP com Bearer token
- [ ] Extração correta de dados AwesomeAPI
- [ ] Identificação de exchange existente
- [ ] POST (criar novo Exchange)
- [ ] PUT (atualizar Exchange existente)
- [ ] Logging de sucesso e erro
- [ ] Retorno de resultado estruturado
- [ ] Testes unitários
- [ ] Testes de integração
- [ ] Documentação de código

---

**Status:** ✅ Especificação Completa - Pronto para Implementação

**Próximos Passos:**
1. Atualizar currency_service.py para incluir atributo `exchange`
2. Implementar ExchangeService conforme esta especificação
3. Integrar com scheduler APScheduler
4. Testar fluxo completo
