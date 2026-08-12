# Cotação Online — Agentes e Skills

Este projeto utiliza agentes e skills do Claude Code para acelerar o desenvolvimento da aplicação FastAPI.

---

## Estrutura

```
.claude/
├── agents/
│   ├── fastapi-developer.md    — orquestrador principal
│   ├── fastapi-scaffold.md     — cria projeto do zero
│   ├── fastapi-endpoint.md     — adiciona novo endpoint
│   ├── http-integration.md     — integra API externa
│   └── openapi-builder.md      — gera documentação OpenAPI
└── skills/
    ├── skill-fastapi-scaffold.md
    ├── skill-fastapi-endpoint.md
    ├── skill-http-integration.md
    └── skill-openapi-builder.md
```

---

## Agentes Disponíveis

### `fastapi-developer`

Agente principal. Use para qualquer tarefa relacionada ao desenvolvimento FastAPI que não se encaixe nos agentes específicos abaixo.

**Exemplos de prompt:**

```
Usando o agente fastapi-developer, qual é a forma correta de
criar uma dependência reutilizável que valida se o usuário
autenticado está ativo antes de acessar qualquer endpoint?
```

```
Usando o agente fastapi-developer, adicione validação de email
duplicado no endpoint de registro de usuário.
```

```
Usando o agente fastapi-developer, crie um middleware que
registra em log o método HTTP, rota e status code de cada
requisição recebida.
```

---

### `fastapi-scaffold`

Cria a estrutura completa de um projeto FastAPI do zero, incluindo autenticação JWT, conexão com PostgreSQL e variáveis de ambiente.

**Exemplo de prompt — scaffold com entidade:**

```
Usando o agente fastapi-scaffold, crie um novo projeto com
as seguintes informações:

projeto: cotacao-online
entidade: Cotacao
campos: simbolo: str, preco: float, moeda: str, data_consulta: datetime
```

**Exemplo de prompt — scaffold vazio:**

```
Usando o agente fastapi-scaffold, crie um novo projeto com
as seguintes informações:

projeto: cotacao-online
scaffold: vazio
```

---

### `fastapi-endpoint`

Adiciona uma nova entidade completa a um projeto FastAPI existente, gerando todas as camadas: model, schema, repository, service e router.

**Exemplo de prompt — endpoint completo:**

```
Usando o agente fastapi-endpoint, adicione uma nova entidade
com as seguintes informações:

entidade: Produto
campos: nome: str, preco: float, descricao: str, disponivel: bool
métodos: GET, POST, PUT, DELETE
```

**Exemplo de prompt — endpoint somente leitura:**

```
Usando o agente fastapi-endpoint, adicione uma nova entidade
com as seguintes informações:

entidade: Categoria
campos: nome: str, descricao: str
métodos: GET
```

**Exemplo de prompt — endpoint sem DELETE:**

```
Usando o agente fastapi-endpoint, adicione uma nova entidade
com as seguintes informações:

entidade: Pedido
campos: numero: str, total: float, status: str, criado_em: datetime
métodos: GET, POST, PUT
```

---

### `http-integration`

Cria a integração com uma API externa usando httpx async, com suporte a autenticação, retry automático em timeout e paginação.

**Exemplo de prompt — API com API Key:**

```
Usando o agente http-integration, crie a integração com
a seguinte API:

api: AwesomeAPI
base_url: https://economia.awesomeapi.com.br
autenticação: api_key
header_name: X-API-Key
endpoints:
  GET /json/{moedas} — retorna cotações das moedas informadas
  GET /json/daily/{moeda}/{dias} — retorna histórico de cotações
paginada: não
```

**Exemplo de prompt — API com Bearer Token:**

```
Usando o agente http-integration, crie a integração com
a seguinte API:

api: BancoCentral
base_url: https://api.bcb.gov.br/dados/serie
autenticação: bearer_token
endpoints:
  GET /bcdata.sgs.{codigo}/dados — retorna série histórica pelo código
paginada: não
timeout: 30
```

**Exemplo de prompt — API paginada:**

```
Usando o agente http-integration, crie a integração com
a seguinte API:

api: MercadoFinanceiro
base_url: https://api.mercado.exemplo.com.br
autenticação: api_key
header_name: Authorization
endpoints:
  GET /ativos — lista todos os ativos disponíveis
  GET /ativos/{ticker}/historico — retorna histórico de preços
paginada: sim
timeout: 20
```

---

### `openapi-builder`

Gera o arquivo `docs/openapi.yml` completo e válido no formato OpenAPI 3.1.0 a partir de um arquivo `SPEC.md` na raiz do projeto.

**Passo 1 — Crie o arquivo `SPEC.md` na raiz do projeto:**

```markdown
# API Spec

## Info
title: Cotação Online API
version: 1.0.0
description: API para consulta e gerenciamento de cotações financeiras
contact:
  name: Time de Desenvolvimento
  email: dev@cotacaoonline.com.br
  url: https://cotacaoonline.com.br/suporte
license:
  name: MIT
  url: https://opensource.org/licenses/MIT
termsOfService: https://cotacaoonline.com.br/termos

## Servers
development: http://localhost:8000
staging: https://staging.api.cotacaoonline.com.br
production: https://api.cotacaoonline.com.br

## Security
type: bearer_jwt

## Tags
- name: Auth
  description: Autenticação e gerenciamento de sessão
- name: Cotações
  description: Consulta de cotações financeiras

## Schemas

### UserCreate
- name: string (required) - Nome completo do usuário
- email: string (required) - Email do usuário
- password: string (required) - Senha com mínimo de 8 caracteres

### UserResponse
- id: uuid (required) - UUID do usuário
- name: string (required) - Nome completo
- email: string (required) - Email do usuário
- is_active: boolean (required) - Status da conta

### TokenResponse
- access_token: string (required) - Bearer token de acesso
- refresh_token: string (required) - Token para renovação
- token_type: string (required) - Tipo do token

## Endpoints

### POST /auth/register
tag: Auth
summary: Registrar novo usuário
security: none
request_body: UserCreate
responses:
  201: UserResponse
request_example:
  name: João Silva
  email: joao@exemplo.com
  password: senha123
response_example:
  201:
    id: 550e8400-e29b-41d4-a716-446655440000
    name: João Silva
    email: joao@exemplo.com
    is_active: true

### POST /auth/login
tag: Auth
summary: Autenticar usuário e obter tokens
security: none
request_body: LoginRequest
responses:
  200: TokenResponse
request_example:
  email: joao@exemplo.com
  password: senha123
response_example:
  200:
    access_token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    refresh_token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    token_type: bearer

### GET /auth/me
tag: Auth
summary: Retorna dados do usuário autenticado
security: bearer
responses:
  200: UserResponse
response_example:
  200:
    id: 550e8400-e29b-41d4-a716-446655440000
    name: João Silva
    email: joao@exemplo.com
    is_active: true
```

**Passo 2 — Execute o agente:**

```
Usando o agente openapi-builder, leia o arquivo SPEC.md
e gere o arquivo docs/openapi.yml.
```

**Exemplo de prompt para atualizar após adicionar endpoints:**

```
Usando o agente openapi-builder, atualizei o SPEC.md com
novos endpoints de Cotações. Regenere o docs/openapi.yml.
```

---

## Stack do Projeto

| Componente       | Tecnologia                          |
|------------------|-------------------------------------|
| Framework        | FastAPI                             |
| Python           | 3.12                                |
| Banco de dados   | PostgreSQL                          |
| ORM              | SQLAlchemy (async) + asyncpg        |
| Autenticação     | JWT — python-jose + passlib[bcrypt] |
| Schemas          | Pydantic v2                         |
| HTTP Client      | httpx (async)                       |
| Configuração     | pydantic-settings + .env            |
| Servidor         | uvicorn                             |
