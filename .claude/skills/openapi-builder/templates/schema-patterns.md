# Template: Geração de Schemas (Request/Response)

Para cada schema declarado em `## Schemas` no SPEC.md, gerar em `components/schemas`. Use `references/type-mapping.md` para traduzir tipos e modificadores de campo.

## Padrão base

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

Campos `optional` **não** entram na lista `required`. Campos com modificadores (`enum`, `default`, `nullable`, constraints) seguem a ordem descrita em `references/type-mapping.md`.

## Campos do tipo lista dentro de schemas

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

## Resposta do tipo lista simples

Para uso em `content` de responses quando o SPEC.md declara `list[NomeDoSchema]` (lista **não paginada**):

```yaml
content:
  application/json:
    schema:
      type: array
      items:
        $ref: '#/components/schemas/{NomeDoSchema}'
```

## Resposta paginada (`paginated[NomeDoSchema]`)

Quando o SPEC.md declara `responses: {código}: paginated[NomeDoSchema]`, gerar um objeto com `items` + `pagination`, referenciando o schema fixo `PaginationMeta` (ver `templates/fixed-components.yml`). Não criar um schema nomeado por endpoint — a estrutura é sempre gerada inline no `content` da resposta:

```yaml
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
          value: {response_example.<código>}
```

Ver `templates/paths-and-parameters.md` para os query params (`page`/`page_size`) que devem ser injetados automaticamente nesse endpoint, e `templates/responses-by-method.md` para o bloco completo de responses de um GET paginado.
