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
request_body: {NomeDoSchema}
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
      tags:
        - {tag}
      summary: {summary}
      description: {description}
      security:
        - {esquema}: []
      parameters: [...]
      requestBody: {...}
      responses: {...}

components:
  securitySchemes: {...}
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

---

## Etapa 4 — Schemas de Request/Response

Para cada schema declarado em `## Schemas` no SPEC.md, gerar em `components/schemas`:

**Mapeamento de tipos:**

| Tipo no SPEC.md | OpenAPI type / format         |
|-----------------|-------------------------------|
| `string`        | `type: string`                |
| `int`           | `type: integer`               |
| `float`         | `type: number` / `format: float` |
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

Para listas (`list[NomeDoSchema]`), usar:

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

```yaml
requestBody:
  required: true
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/{NomeDoSchema}'
      example:
        {campos do request_example}
```

---

## Etapa 6 — Respostas Padrão por Método HTTP

Sempre incluir os códigos abaixo para cada método. Se o endpoint declarar respostas adicionais no SPEC.md, incluí-las junto.

### GET
```yaml
responses:
  '200':
    description: Sucesso
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/{NomeDoSchema}'
        example: {response_example.200}
  '400':
    description: Requisição inválida
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/ErrorResponse'
  '401':
    description: Não autenticado
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/ErrorResponse'
  '500':
    description: Erro interno do servidor
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/ErrorResponse'
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
        example: {response_example.201}
  '400':
    description: Requisição inválida
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/ErrorResponse'
  '401':
    description: Não autenticado
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/ErrorResponse'
  '404':
    description: Recurso não encontrado
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/ErrorResponse'
  '500':
    description: Erro interno do servidor
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/ErrorResponse'
```

### PUT / PATCH / DELETE
Mesmos códigos que POST (201 vira 200 para PUT/PATCH, e 204 sem body para DELETE).

**DELETE sem body de resposta:**
```yaml
  '204':
    description: Removido com sucesso
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
2. **Nunca escreva schemas inline** nos paths — sempre use `$ref: '#/components/schemas/{Nome}'`
3. **Sempre inclua `ErrorResponse`** em `components/schemas`, mesmo que o SPEC.md não declare
4. **Sempre inclua os códigos de resposta padrão** do método HTTP, mesmo que não declarados no SPEC.md
5. **Se o endpoint não declarar `security`**, pergunte ao usuário antes de assumir
6. **Se um schema referenciado em `responses` não estiver declarado em `## Schemas`**, avise o usuário e gere um schema vazio com comentário `# TODO: definir campos`
7. **Sempre valide se o YAML gerado é sintaticamente correto** antes de salvar — indentação e estrutura devem estar perfeitas
8. **Ao final**, informe ao usuário o caminho do arquivo gerado e a lista de endpoints documentados
