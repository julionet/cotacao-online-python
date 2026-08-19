# Template: `.spectralrc.yml`

Este arquivo descreve o `.spectralrc.yml` que deve ser criado **na raiz do projeto**, ao lado de `docs/openapi.yml`, logo após o YAML ser salvo. Ele contém as regras do [Spectral](https://github.com/stoplightio/spectral) que validam se `docs/openapi.yml` respeita exatamente as convenções desta skill (as mesmas descritas em "Regras de Execução" no `SKILL.md` e em "Verificações Antes de Salvar" no agente).

Gere o arquivo sempre com este conteúdo (ajuste apenas se o SPEC.md não usar paginação — nesse caso, ainda assim mantenha a regra `openapi-pagination-params`, pois ela só afeta endpoints paginados via `given`):

```yaml
extends:
  - spectral:oas

rules:
  # operationId deve seguir {httpMethod}{PathSegments} em camelCase
  openapi-operationid-camelcase:
    description: operationId deve estar em camelCase, único em todo o arquivo
    given: "$.paths[*][get,put,post,delete,patch].operationId"
    severity: error
    then:
      function: casing
      functionOptions:
        type: camel

  # X-Request-ID deve ser referenciado em todo endpoint
  openapi-request-id-required:
    description: Todo endpoint deve referenciar components/parameters/RequestId em parameters
    given: "$.paths[*][get,put,post,delete,patch]"
    severity: error
    then:
      field: parameters
      function: schema
      functionOptions:
        schema:
          type: array
          contains:
            type: object
            properties:
              $ref:
                const: "#/components/parameters/RequestId"

  # Proibir nullable: true (sintaxe OpenAPI 3.0) — usar type: [tipo, "null"]
  openapi-no-nullable-true:
    description: "Campos nullable devem usar type: [tipo, 'null'], nunca nullable: true"
    given: "$..[?(@property === 'nullable')]"
    severity: error
    then:
      function: undefined

  # Respostas de erro padrão sempre via $ref, nunca inline
  openapi-error-responses-ref:
    description: Respostas 400/401/403/404/422/500 devem usar $ref para components/responses
    given: "$.paths[*][get,put,post,delete,patch].responses['400','401','403','404','422','500']"
    severity: error
    then:
      field: $ref
      function: truthy

  # examples (plural) com chave default — nunca example (singular)
  openapi-examples-plural-default:
    description: "Usar 'examples' (plural) com chave 'default'; nunca 'example' (singular)"
    given: "$..content[application/json]"
    severity: error
    then:
      - field: example
        function: undefined
      - field: examples.default
        function: truthy

  # GET/DELETE não podem ter requestBody
  openapi-no-requestbody-get-delete:
    description: Endpoints GET e DELETE não devem ter requestBody
    given: "$.paths[*][get,delete]"
    severity: error
    then:
      field: requestBody
      function: undefined

  # ErrorResponse e PaginationMeta sempre presentes em components/schemas
  openapi-required-schemas:
    description: components/schemas deve conter ErrorResponse e PaginationMeta
    given: "$.components.schemas"
    severity: error
    then:
      - field: ErrorResponse
        function: truthy
      - field: PaginationMeta
        function: truthy

  # As 6 respostas de erro padrão sempre presentes em components/responses
  openapi-required-error-responses:
    description: components/responses deve conter os 6 erros padrão
    given: "$.components.responses"
    severity: error
    then:
      - field: BadRequest
        function: truthy
      - field: Unauthorized
        function: truthy
      - field: Forbidden
        function: truthy
      - field: NotFound
        function: truthy
      - field: UnprocessableEntity
        function: truthy
      - field: InternalServerError
        function: truthy

  # RequestId sempre declarado em components/parameters
  openapi-requestid-component-exists:
    description: components/parameters deve conter RequestId
    given: "$.components.parameters"
    severity: error
    then:
      field: RequestId
      function: truthy

  # Endpoints com resposta paginada devem referenciar PageParam e PageSizeParam
  openapi-pagination-params:
    description: Endpoints com resposta paginada (schema contém "pagination") devem referenciar PageParam e PageSizeParam
    given: "$.paths[*][get,put,post,delete,patch][?(@.responses['200'].content['application/json'].schema.properties.pagination)]"
    severity: warn
    then:
      field: parameters
      function: schema
      functionOptions:
        schema:
          type: array
          minItems: 3

  # security deve estar explícito em todo endpoint (bearer, api_key ou [])
  openapi-security-explicit:
    description: Todo endpoint deve declarar security explicitamente (nunca herdar implicitamente sem revisão)
    given: "$.paths[*][get,put,post,delete,patch]"
    severity: warn
    then:
      field: security
      function: defined
```

## Como aplicar

1. Salve o conteúdo acima como `.spectralrc.yml` na raiz do projeto (mesmo nível de `SPEC.md`), logo após salvar `docs/openapi.yml`.
2. Se `.spectralrc.yml` já existir, pergunte ao usuário se deseja **sobrescrever** ou **manter** o arquivo existente — não decida isso sozinho (mesma regra aplicada a `docs/openapi.yml`).
3. Informe ao usuário que a validação pode ser executada com `npx @stoplight/spectral-cli lint docs/openapi.yml` (requer Node.js instalado; a skill não executa o comando automaticamente).
