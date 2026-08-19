# Template: Paths e Parâmetros

## `operationId`

Gerar um `operationId` único para cada endpoint seguindo a convenção `{httpMethod}{PathSegments}` em camelCase:
- Método HTTP em minúsculas
- Segmentos do path em PascalCase
- Substituir `{param}` por `By{Param}` (ex: `{id}` → `ById`)

| Endpoint              | operationId        |
|-----------------------|---------------------|
| `POST /auth/register` | `postAuthRegister`  |
| `GET /auth/me`        | `getAuthMe`         |
| `GET /users/{id}`     | `getUserById`       |
| `PUT /users/{id}`     | `putUserById`       |
| `DELETE /users/{id}`  | `deleteUserById`    |
| `GET /orders`         | `getOrders`         |

`operationId` deve ser único em todo o arquivo. Se dois endpoints gerarem o mesmo valor (ex: dois `GET /x/{id}` em grupos diferentes), avise o usuário e resolva o conflito acrescentando o `tag` ao nome.

## `X-Request-ID` (sempre incluir em todos os endpoints)

Referenciar o parâmetro definido em `components/parameters`. Deve ser o primeiro item da lista de `parameters` de cada endpoint:

```yaml
parameters:
  - $ref: '#/components/parameters/RequestId'
```

## Paginação — injeção automática de query params

Se `responses` do endpoint declarar `paginated[NomeDoSchema]` (sempre em métodos `GET`), injetar os dois parâmetros abaixo **logo após** `RequestId` e **antes** de qualquer `query_params` declarado manualmente no SPEC.md:

```yaml
parameters:
  - $ref: '#/components/parameters/RequestId'
  - $ref: '#/components/parameters/PageParam'
  - $ref: '#/components/parameters/PageSizeParam'
  # ...demais query_params do SPEC.md, se houver
```

## Path params

```yaml
parameters:
  - name: {param}
    in: path
    required: true
    schema:
      type: {tipo}
    description: {descrição}
```

## Query params

```yaml
parameters:
  - name: {param}
    in: query
    required: {true|false}
    schema:
      type: {tipo}
    description: {descrição}
```

## Header params

```yaml
parameters:
  - name: {header}
    in: header
    required: {true|false}
    schema:
      type: {tipo}
    description: {descrição}
```

## Request body

O campo `content_type` no SPEC.md define o Content-Type do endpoint (padrão: `application/json`). **Nunca gerar `requestBody` para `GET` ou `DELETE`** — se o SPEC.md declarar `request_body` nesses métodos, avise o usuário antes de ignorar.

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

