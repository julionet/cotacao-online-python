# Skill: Integração com API Externa via httpx

Você é responsável por criar a integração com uma API externa em um projeto Python. Siga as instruções abaixo com precisão.

Esta skill está dividida em vários arquivos. Leia cada um deles no momento indicado pela etapa correspondente — não é necessário carregar todos de uma vez.

```
.claude/skills/http-integration/
├── SKILL.md                  (este arquivo — fluxo principal e regras de execução)
├── base-client.md            (base_client.py — criado uma única vez por projeto)
├── api-client-template.md    ({api_name}_client.py — paginado e não paginado)
├── environment-config.md     (variáveis .env/.env.example + campos em config.py)
└── service-integration.md    (como instanciar o client no service)
```

## Como Invocar

O usuário deve fornecer:

```
api: {NomeDaApi}
base_url: {URL base da API}
autenticação: api_key | bearer_token | oauth2 | nenhuma
header_name: {nome do header}         (apenas para api_key)
token_url: {URL do endpoint de token} (apenas para oauth2)
client_id: {client id}                (apenas para oauth2)
client_secret: {client secret}        (apenas para oauth2)
endpoints: {descrição dos endpoints a consumir}
timeout: {segundos}  (opcional, padrão 20)
paginada: sim | não
```

**Exemplo:**
```
api: ViaCep
base_url: https://viacep.com.br/ws
autenticação: nenhuma
endpoints: GET /{cep}/json – busca endereço por CEP
paginada: não
```

## O Que Esta Skill Faz

1. Verifica se `app/integrations/` existe — cria (com `__init__.py`) se não existir
2. Verifica se `app/integrations/base_client.py` existe — cria se não existir
3. Cria `app/integrations/{api_name}_client.py`
4. Adiciona variáveis ao `.env` e `.env.example`
5. Adiciona campos em `app/core/config.py`
6. Orienta como instanciar o client no service correspondente

## Etapa 1 — Base Client

Leia `base-client.md` e, **apenas se `app/integrations/base_client.py` ainda não existir**, crie-o exatamente como especificado. Se já existir, não o sobrescreva — ele é compartilhado por todas as integrações do projeto.

## Etapa 2 — Client da API

Leia `api-client-template.md` e gere `app/integrations/{api_name}_client.py`, escolhendo o padrão paginado ou não paginado conforme informado na invocação.

## Etapa 3 — Variáveis de Ambiente e Config

Leia `environment-config.md` e:
- adicione as variáveis correspondentes ao tipo de autenticação em `.env` e `.env.example`
- adicione os campos correspondentes em `app/core/config.py`

## Etapa 4 — Integração no Service

Leia `service-integration.md` e oriente (ou implemente, se solicitado) como instanciar o client no service correspondente.

## Regras de Execução

1. **Nunca instanciar o client no router** — sempre no service
2. **Nunca mapear a resposta para Pydantic** nesta camada — retornar `dict | list` bruto
3. **Nunca fazer retry em erros 4xx** — retry apenas em `TimeoutException`, `httpx.RequestError` genérico (falha de conexão) e status 502/503/504
4. **Retry usa backoff exponencial fixo `(1, 2, 4)` segundos** — mesmo padrão usado em `app/services/exchange_service.py` (`_BACKOFF`), não um `retry_wait` fixo configurável
5. **Erros de rede genéricos (`httpx.RequestError`) e JSON malformado na resposta também viram `HTTPException`** (502 Bad Gateway) — nunca deixe uma exceção não controlada propagar do client
6. **Sempre logar** tentativas com falha (`logger.warning`) e erros finais (`logger.error`) no `base_client.py`, no mesmo padrão de `logger = logging.getLogger(__name__)` já usado no restante do projeto
7. **Sempre adicionar as variáveis ao `.env.example`** ao criar um novo client
8. **Sempre usar `settings`** para URL base, token e timeout — nunca hardcode
9. **Campos opcionais em `config.py`** (tokens, api keys, client secrets) usam default `str = ""` — nunca `str | None = None` — para seguir o padrão já usado em `AIRTABLE_TOKEN`, `MAKE_WEBHOOK_URL` etc.
10. **Para APIs paginadas**, o client expõe uma página por chamada — o service decide quantas páginas buscar
11. **O nome do header de API Key é sempre configurável** via variável de ambiente — nunca fixo no código
12. **Para OAuth2**, o token é cacheado na instância e renovado automaticamente 30 segundos antes de expirar
13. **O client expõe `get`, `post`, `post_form`, `put`, `patch` e `delete`** — inclua `patch` mesmo que a invocação atual não peça, pois faz parte da interface padrão do `BaseHttpClient`
14. **Sempre informar ao usuário** quais variáveis precisam ser preenchidas no `.env` ao final
