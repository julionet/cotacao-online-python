# Skill: Gerar arquivo OpenAPI 3.1.0 em YAML

Você é responsável por ler um arquivo `SPEC.md` fornecido pelo usuário e gerar um arquivo `docs/openapi.yml` completo e válido no formato OpenAPI 3.1.0.

---

## Etapa 1 — Leitura do SPEC.md

Antes de gerar qualquer coisa, leia o arquivo `SPEC.md` na raiz do projeto. Se ele não existir, informe ao usuário e apresente o formato esperado (descrito abaixo) para que ele o crie.

---

## Formato Esperado do SPEC.md

O usuário deve criar um arquivo `SPEC.md` na raiz do projeto com a seguinte estrutura:

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
  {código}: {NomeDoSchema | list[NomeDoSchema]}
  {código}: {descrição livre para erros específicos}
request_example:
  {campo}: {valor de exemplo}
response_example:
  {código}:
    {campo}: {valor de exemplo}
```

**Exemplo real de SPEC.md:**

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
- id: string (required) - UUID do usuário
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

---

## Etapa 2 — Estrutura do arquivo `docs/openapi.yml`

Gere o arquivo seguindo exatamente esta estrutura:

```yaml
openapi: 3.1.0

info:
  title: {title}
  version: {version}
  description: {description}
  termsOfService: {termsOfService}
  contact:
    name: {contact.name}
    email: {contact.email}
    url: {contact.url}
  license:
    name: {license.name}
    url: {license.url}

servers:
  - url: {development}
    description: Development
  - url: {staging}
    description: Staging
  - url: {production}
    description: Production

tags:
  - name: {tag.name}
    description: {tag.description}

paths:
  {/caminho}:
    {método}:
      operationId: {operationId}
      tags:
        - {tag}
      summary: {summary}
      description: {description}
      security:
        - {esquema}: []
      parameters:
        - $ref: '#/components/parameters/RequestId'
        - ...
      requestBody: {...}
      responses: {...}

components:
  securitySchemes: {...}
  parameters: {...}
  responses: {...}
  schemas: {...}
```

---

## Etapa 3 — Componentes Fixos (sempre incluir)

### `components/schemas/ErrorResponse`

Sempre incluir este schema. É referenciado por todos os erros padrão:

```yaml
ErrorResponse:
  type: object
  required:
    - detail
  properties:
    detail:
      type: string
      description: Descrição do erro
  example:
    detail: Recurso não encontrado
```

### `components/securitySchemes`

Incluir conforme o tipo definido em `Security` no SPEC.md:

**bearer_jwt:**
```yaml
BearerAuth:
  type: http
  scheme: bearer
  bearerFormat: JWT
  description: Token JWT obtido via POST /auth/login
```

**api_key:**
```yaml
ApiKeyAuth:
  type: apiKey
  in: header
  name: {api_key_header}
  description: API Key enviada no header {api_key_header}
```

**ambos:** incluir os dois blocos acima.

### `components/parameters/RequestId`

Sempre incluir este parâmetro. É referenciado por todos os endpoints:

```yaml
RequestId:
  name: X-Request-ID
  in: header
  required: false
  schema:
    type: string
    format: uuid
  description: Identificador único da requisição no formato UUID
  example: 550e8400-e29b-41d4-a716-446655440000
```

### `components/responses`

Sempre incluir estas respostas de erro padrão. São referenciadas por todos os endpoints via `$ref`:

```yaml
BadRequest:
  description: Requisição inválida
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/ErrorResponse'
      examples:
        default:
          summary: Exemplo padrão
          value:
            detail: Requisição inválida

Unauthorized:
  description: Não autenticado
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/ErrorResponse'
      examples:
        default:
          summary: Exemplo padrão
          value:
            detail: Não autenticado

NotFound:
  description: Recurso não encontrado
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/ErrorResponse'
      examples:
        default:
          summary: Exemplo padrão
          value:
            detail: Recurso não encontrado

UnprocessableEntity:
  description: Entidade não processável — erro de validação dos dados enviados
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/ErrorResponse'
      examples:
        default:
          summary: Exemplo padrão
          value:
            detail: Dados inválidos ou ausentes

Forbidden:
  description: Acesso proibido — autenticado mas sem permissão para este recurso
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/ErrorResponse'
      examples:
        default:
          summary: Exemplo padrão
          value:
            detail: Acesso proibido

InternalServerError:
  description: Erro interno do servidor
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/ErrorResponse'
      examples:
        default:
          summary: Exemplo padrão
          value:
            detail: Erro interno do servidor
```

---

## Etapa 4 — Schemas de Request/Response

Para cada schema declarado em `## Schemas` no SPEC.md, gerar em `components/schemas`:

**Mapeamento de tipos:**

| Tipo no SPEC.md | OpenAPI type / format         |
|-----------------|-------------------------------|
| `string`        | `type: string`                |
| `int`           | `type: integer`               |
| `float`         | `type: number` / `format: float` |
| `double`        | `type: number` / `format: double` |
| `bool`/`boolean`| `type: boolean`               |
| `uuid`          | `type: string` / `format: uuid` |
| `date`          | `type: string` / `format: date` |
| `datetime`      | `type: string` / `format: date-time` |
| `email`         | `type: string` / `format: email` |

**Padrão de geração:**

```yaml
{NomeDoSchema}:
  type: object
  required:
    - {campos marcados como required}
  properties:
    {campo}:
      type: {tipo mapeado}
      description: {descrição}
```

**Campos do tipo lista dentro de schemas:**

Para `list[tipo primitivo]` (ex: `list[string]`, `list[int]`):

```yaml
{campo}:
  type: array
  items:
    type: {tipo mapeado}
  description: {descrição}
```

Para `list[NomeDoSchema]` (ex: `list[ItemSchema]`):

```yaml
{campo}:
  type: array
  items:
    $ref: '#/components/schemas/{NomeDoSchema}'
  description: {descrição}
```

**Resposta do tipo lista** — para uso em `content` de responses quando o SPEC.md declara `list[NomeDoSchema]`:

```yaml
content:
  application/json:
    schema:
      type: array
      items:
        $ref: '#/components/schemas/{NomeDoSchema}'
```

---

## Etapa 5 — Paths e Parâmetros

### `operationId`

Gerar um `operationId` único para cada endpoint seguindo a convenção `{httpMethod}{PathSegments}` em camelCase:
- Método HTTP em minúsculas
- Segmentos do path em PascalCase
- Substituir `{param}` por `By{Param}` (ex: `{id}` → `ById`)

| Endpoint              | operationId        |
|-----------------------|--------------------|
| `POST /auth/register` | `postAuthRegister` |
| `GET /auth/me`        | `getAuthMe`        |
| `GET /users/{id}`     | `getUserById`      |
| `PUT /users/{id}`     | `putUserById`      |
| `DELETE /users/{id}`  | `deleteUserById`   |
| `GET /orders`         | `getOrders`        |

### `X-Request-ID` (sempre incluir em todos os endpoints)

Referenciar o parâmetro definido em `components/parameters`. Deve ser o primeiro item da lista de `parameters` de cada endpoint:

```yaml
parameters:
  - $ref: '#/components/parameters/RequestId'
```

### Path params

```yaml
parameters:
  - name: {param}
    in: path
    required: true
    schema:
      type: {tipo}
    description: {descrição}
```

### Query params

```yaml
parameters:
  - name: {param}
    in: query
    required: {true|false}
    schema:
      type: {tipo}
    description: {descrição}
```

### Header params

```yaml
parameters:
  - name: {header}
    in: header
    required: {true|false}
    schema:
      type: {tipo}
    description: {descrição}
```

### Request body

O campo `content_type` no SPEC.md define o Content-Type do endpoint (padrão: `application/json`).

**`application/json` (padrão):**

```yaml
requestBody:
  required: true
  description: {request_body_description se declarado no SPEC.md; omitir se ausente}
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/{NomeDoSchema}'
      examples:
        default:
          summary: Exemplo padrão
          value:
            {campos do request_example}
```

**`application/x-www-form-urlencoded`:**

```yaml
requestBody:
  required: true
  description: {request_body_description se declarado no SPEC.md; omitir se ausente}
  content:
    application/x-www-form-urlencoded:
      schema:
        $ref: '#/components/schemas/{NomeDoSchema}'
      examples:
        default:
          summary: Exemplo padrão
          value:
            {campos do request_example}
```

---

## Etapa 6 — Respostas Padrão por Método HTTP

Sempre incluir os códigos abaixo para cada método. Se o endpoint declarar respostas adicionais no SPEC.md, incluí-las junto.

### GET

**Se a resposta for um objeto único:**

```yaml
responses:
  '200':
    description: Sucesso
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/{NomeDoSchema}'
        examples:
          default:
            summary: Exemplo padrão
            value: {response_example.200}
  '400':
    $ref: '#/components/responses/BadRequest'
  '401':
    $ref: '#/components/responses/Unauthorized'
  '403':
    $ref: '#/components/responses/Forbidden'
  '404':
    $ref: '#/components/responses/NotFound'
  '500':
    $ref: '#/components/responses/InternalServerError'
```

**Se a resposta for uma lista (`list[NomeDoSchema]`):**

```yaml
responses:
  '200':
    description: Sucesso
    content:
      application/json:
        schema:
          type: array
          items:
            $ref: '#/components/schemas/{NomeDoSchema}'
        examples:
          default:
            summary: Exemplo padrão
            value: [{response_example.200}]
  '400':
    $ref: '#/components/responses/BadRequest'
  '401':
    $ref: '#/components/responses/Unauthorized'
  '403':
    $ref: '#/components/responses/Forbidden'
  '500':
    $ref: '#/components/responses/InternalServerError'
```

### POST
```yaml
responses:
  '201':
    description: Criado com sucesso
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/{NomeDoSchema}'
        examples:
          default:
            summary: Exemplo padrão
            value: {response_example.201}
  '400':
    $ref: '#/components/responses/BadRequest'
  '401':
    $ref: '#/components/responses/Unauthorized'
  '403':
    $ref: '#/components/responses/Forbidden'
  '404':
    $ref: '#/components/responses/NotFound'
  '422':
    $ref: '#/components/responses/UnprocessableEntity'
  '500':
    $ref: '#/components/responses/InternalServerError'
```

### PUT / PATCH
```yaml
responses:
  '200':
    description: Atualizado com sucesso
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/{NomeDoSchema}'
        examples:
          default:
            summary: Exemplo padrão
            value: {response_example.200}
  '400':
    $ref: '#/components/responses/BadRequest'
  '401':
    $ref: '#/components/responses/Unauthorized'
  '403':
    $ref: '#/components/responses/Forbidden'
  '404':
    $ref: '#/components/responses/NotFound'
  '422':
    $ref: '#/components/responses/UnprocessableEntity'
  '500':
    $ref: '#/components/responses/InternalServerError'
```

### DELETE
```yaml
responses:
  '204':
    description: Removido com sucesso
  '400':
    $ref: '#/components/responses/BadRequest'
  '401':
    $ref: '#/components/responses/Unauthorized'
  '403':
    $ref: '#/components/responses/Forbidden'
  '404':
    $ref: '#/components/responses/NotFound'
  '500':
    $ref: '#/components/responses/InternalServerError'
```

---

## Etapa 7 — Security por Endpoint

**Endpoint com `security: bearer`:**
```yaml
security:
  - BearerAuth: []
```

**Endpoint com `security: api_key`:**
```yaml
security:
  - ApiKeyAuth: []
```

**Endpoint com `security: none`:**
```yaml
security: []
```

---

## Etapa 8 — Onde Salvar

Criar o diretório `docs/` se não existir. Salvar como `docs/openapi.yml`.

---

## Regras de Execução

1. **Sempre leia o SPEC.md completo** antes de começar a gerar o YAML
2. **Nunca escreva schemas ou respostas de erro inline** nos paths — sempre use `$ref: '#/components/schemas/{Nome}'` para schemas e `$ref: '#/components/responses/{Nome}'` para erros padrão
3. **Sempre inclua `ErrorResponse`** em `components/schemas`, mesmo que o SPEC.md não declare
4. **Sempre inclua os códigos de resposta padrão** do método HTTP, mesmo que não declarados no SPEC.md
5. **Se o endpoint não declarar `security`**, pergunte ao usuário antes de assumir
6. **Se um schema referenciado em `responses` não estiver declarado em `## Schemas`**, avise o usuário e gere um schema vazio com comentário `# TODO: definir campos`
7. **Sempre valide se o YAML gerado é sintaticamente correto** antes de salvar — indentação e estrutura devem estar perfeitas
8. **Ao final**, informe ao usuário o caminho do arquivo gerado e a lista de endpoints documentados
9. **Sempre inclua `operationId`** em cada endpoint seguindo a convenção `{httpMethod}{PathSegments}` em camelCase — deve ser único em todo o arquivo
10. **Sempre inclua `X-Request-ID`** em `components/parameters/RequestId` e referencie com `$ref: '#/components/parameters/RequestId'` como primeiro parâmetro de todos os endpoints
11. **Sempre inclua os erros padrão em `components/responses`** e referencie-os via `$ref` — nunca inline. Use `examples` (plural) com chave `default` para todos os exemplos de request/response
