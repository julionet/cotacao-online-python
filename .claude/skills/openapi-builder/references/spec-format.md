# Referência: Formato do SPEC.md

O usuário deve criar um arquivo `SPEC.md` na raiz do projeto com a seguinte estrutura.

```markdown
# API Spec

## Info
title: {Título da API}
version: {ex: 1.0.0}
description: {Descrição da API}
contact:
  name: {Nome do contato}
  email: {email@exemplo.com}
  url: {https://exemplo.com/suporte}
license:
  name: {ex: MIT}
  url: {https://opensource.org/licenses/MIT}
termsOfService: {https://exemplo.com/termos}

## Servers
development: {http://localhost:8000}
staging: {https://staging.api.exemplo.com}
production: {https://api.exemplo.com}

## Security
type: bearer_jwt | api_key | ambos
api_key_header: {X-API-Key}  # obrigatório apenas para api_key

## Tags
- name: {NomeDoGrupo}
  description: {Descrição do grupo de endpoints}

## Schemas

### {NomeDoSchema}
- {campo}: {tipo} ({required|optional}) - {descrição}
- {campo}: list[{tipo}] ({required|optional}) - {descrição}
- {campo}: list[{NomeDoSchema}] ({required|optional}) - {descrição}
- {campo}: {tipo} ({required|optional}) [{modificadores}] - {descrição}

## Endpoints

### {MÉTODO} {/caminho}
tag: {NomeDoGrupo}
summary: {Resumo do endpoint}
description: {Descrição detalhada (opcional)}
security: bearer | api_key | none
path_params:
  {param}: {tipo} - {descrição}
query_params:
  {param}: {tipo} ({required|optional}) - {descrição}
header_params:
  {header}: {tipo} ({required|optional}) - {descrição}
content_type: application/json | application/x-www-form-urlencoded  # opcional, padrão: application/json
request_body: {NomeDoSchema}
request_body_description: {Descrição do corpo da requisição}  # opcional
responses:
  {código}: {NomeDoSchema | list[NomeDoSchema] | paginated[NomeDoSchema]}
  {código}: {descrição livre para erros específicos}
request_example:
  {campo}: {valor de exemplo}
response_example:
  {código}:
    {campo}: {valor de exemplo}
```

---

## Modificadores de campo (`[...]`)

Todo campo de schema pode receber um bloco opcional `[...]` entre o `(required|optional)` e o `-`, com modificadores separados por vírgula. Ver `references/type-mapping.md` para a tradução exata de cada modificador para YAML.

Modificadores suportados:

| Modificador | Aplica-se a | Exemplo |
|---|---|---|
| `nullable` | qualquer tipo | `[nullable]` |
| `enum: v1,v2,v3` | `string`, `int` | `[enum: active,inactive,pending]` |
| `default: valor` | qualquer tipo | `[default: user]` |
| `minLength: n` / `maxLength: n` | `string` | `[minLength: 8, maxLength: 64]` |
| `pattern: regex` | `string` | `[pattern: ^[0-9]{11}$]` |
| `minimum: n` / `maximum: n` | `int`, `float`, `double` | `[minimum: 0, maximum: 150]` |

Múltiplos modificadores no mesmo campo são combinados: `[nullable, enum: user,admin, default: user]`.

---

## Endpoints de lista paginada (`paginated[NomeDoSchema]`)

Quando um endpoint `GET` declara `responses: 200: paginated[NomeDoSchema]`, a skill:

- injeta automaticamente os parâmetros de query reutilizáveis `PageParam` e `PageSizeParam` (ver `templates/fixed-components.yml`), antes de quaisquer `query_params` declarados manualmente;
- gera a resposta como um objeto `items` (array de `$ref` ao schema) + `pagination` (`$ref` para `PaginationMeta`) — ver `templates/responses-by-method.md`.

Não é necessário declarar `PaginationMeta` em `## Schemas` — ela é um componente fixo, igual ao `ErrorResponse`.

---

## Exemplo real de SPEC.md

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
- name: string (required) [minLength: 3, maxLength: 120] - Nome completo do usuário
- email: string (required) [pattern: ^[^@]+@[^@]+\.[^@]+$] - Email do usuário
- password: string (required) [minLength: 8] - Senha com mínimo de 8 caracteres
- role: string (optional) [enum: user,admin, default: user] - Papel do usuário

### UserResponse
- id: string (required) - UUID do usuário
- name: string (required) - Nome completo
- email: string (required) - Email do usuário
- is_active: boolean (required) - Status da conta
- deleted_at: datetime (optional) [nullable] - Data de exclusão lógica, se houver

### TokenResponse
- access_token: string (required) - Bearer token de acesso
- refresh_token: string (required) - Token para renovação
- token_type: string (required) - Tipo do token

### CotacaoResponse
- symbol: string (required) - Código do ativo
- price: float (required) [minimum: 0] - Preço atual
- currency: string (required) [enum: BRL,USD,EUR] - Moeda da cotação
- updated_at: datetime (required) - Data/hora da última atualização

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

### GET /cotacoes
tag: Cotações
summary: Lista cotações disponíveis, paginado
security: bearer
query_params:
  symbol: string (optional) - Filtra por código do ativo
responses:
  200: paginated[CotacaoResponse]
response_example:
  200:
    items:
      - symbol: PETR4
        price: 38.42
        currency: BRL
        updated_at: 2026-08-18T13:00:00Z
    pagination:
      page: 1
      page_size: 20
      total_items: 1
      total_pages: 1
```
