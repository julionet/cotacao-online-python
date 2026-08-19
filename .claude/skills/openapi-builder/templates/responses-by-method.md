# Template: Respostas Padrão por Método HTTP

Sempre incluir os códigos abaixo para cada método. Se o endpoint declarar respostas adicionais no SPEC.md, incluí-las junto.

## GET

**Se a resposta for um objeto único (`responses: 200: NomeDoSchema`):**

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

**Se a resposta for uma lista simples (`responses: 200: list[NomeDoSchema]`):**

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

**Se a resposta for paginada (`responses: 200: paginated[NomeDoSchema]`):**

Ver `templates/schema-patterns.md` para o formato do `schema` inline (`items` + `pagination`), e `templates/paths-and-parameters.md` para os parâmetros `PageParam`/`PageSizeParam` injetados automaticamente.

```yaml
responses:
  '200':
    description: Sucesso
    content:
      application/json:
        schema:
          type: object
          required:
            - items
            - pagination
          properties:
            items:
              type: array
              items:
                $ref: '#/components/schemas/{NomeDoSchema}'
            pagination:
              $ref: '#/components/schemas/PaginationMeta'
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
  '500':
    $ref: '#/components/responses/InternalServerError'
```

## POST
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

## PUT / PATCH
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

## DELETE
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
