# Variáveis de Ambiente e `app/core/config.py`

## Variáveis de Ambiente

Adicionar ao `.env` e `.env.example` da aplicação. Siga o padrão de comentário de seção já usado no projeto (ex.: `# Integração com Airtable`).

**API Key:**
```
{API_NAME}_BASE_URL=https://api.exemplo.com
{API_NAME}_API_KEY=sua-api-key
{API_NAME}_KEY_HEADER=X-API-Key
{API_NAME}_TIMEOUT=20
```

**Bearer Token:**
```
{API_NAME}_BASE_URL=https://api.exemplo.com
{API_NAME}_TOKEN=seu-bearer-token
{API_NAME}_TIMEOUT=20
```

**OAuth2 Client Credentials:**
```
{API_NAME}_BASE_URL=https://api.exemplo.com
{API_NAME}_TOKEN_URL=https://auth.exemplo.com/oauth/token
{API_NAME}_CLIENT_ID=seu-client-id
{API_NAME}_CLIENT_SECRET=seu-client-secret
{API_NAME}_TIMEOUT=20
```

**Sem autenticação:**
```
{API_NAME}_BASE_URL=https://api.exemplo.com
{API_NAME}_TIMEOUT=20
```

No `.env` real (nunca criado por esta skill, apenas orientado), o usuário preenche os valores reais. No `.env.example`, use valores de exemplo/placeholder como os já existentes no projeto (ex.: `seu-token-airtable-aqui`).

## Campos em `app/core/config.py`

Adicionar à classe `Settings` (`pydantic_settings.BaseSettings`). Campos opcionais (tokens, api keys, client secrets, header names, URLs de auth) usam default `str = ""` — **nunca `str | None = None`** — para seguir o padrão já usado em `AIRTABLE_TOKEN`, `MAKE_WEBHOOK_URL` e demais integrações existentes no projeto.

```python
# Comum
{API_NAME}_BASE_URL: str
{API_NAME}_TIMEOUT: int = 20

# API Key
{API_NAME}_API_KEY: str = ""
{API_NAME}_KEY_HEADER: str = ""

# Bearer Token
{API_NAME}_TOKEN: str = ""

# OAuth2
{API_NAME}_TOKEN_URL: str = ""
{API_NAME}_CLIENT_ID: str = ""
{API_NAME}_CLIENT_SECRET: str = ""
```

Inclua apenas os campos do bloco de autenticação escolhido (`API Key`, `Bearer Token` ou `OAuth2`), além do bloco `Comum`. Se `autenticação: nenhuma`, inclua apenas o bloco `Comum`.

## Regras

1. `{API_NAME}_BASE_URL` nunca tem default — é sempre obrigatório
2. `{API_NAME}_TIMEOUT` tem default `20`, sobrescrito apenas se o usuário informar um valor diferente na invocação
3. Adicione um comentário acima do bloco novo em `config.py` identificando a API (ex.: `# Integração com {NomeDaApi}`), no mesmo padrão dos blocos já existentes
4. Nunca remova ou reordene campos já existentes em `Settings` — apenas acrescente o novo bloco ao final da classe, antes de `model_config`
