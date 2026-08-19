# Skill: Gerar arquivo OpenAPI 3.1.0 em YAML

Você é responsável por ler um arquivo `SPEC.md` fornecido pelo usuário e gerar um arquivo `docs/openapi.yml` completo e válido no formato OpenAPI 3.1.0.

Esta skill está dividida em vários arquivos. Leia cada um deles no momento indicado pela etapa correspondente — não é necessário carregar todos de uma vez.

```
.claude/skills/openapi-builder/
├── SKILL.md                              (este arquivo — fluxo principal)
├── references/
│   ├── spec-format.md                    (formato do SPEC.md + exemplo real)
│   └── type-mapping.md                   (tipos primitivos + modificadores de campo)
└── templates/
    ├── fixed-components.yml              (ErrorResponse, security, RequestId, paginação, erros padrão)
    ├── schema-patterns.md                (geração de components/schemas)
    ├── paths-and-parameters.md           (operationId, parâmetros, requestBody)
    ├── responses-by-method.md            (respostas padrão por método HTTP)
    └── spectral-rules.md                 (regras do .spectralrc.yml gerado após o openapi.yml)
```

---

## Etapa 1 — Leitura do SPEC.md

Antes de gerar qualquer coisa, leia o arquivo `SPEC.md` na raiz do projeto. Se ele não existir, leia `references/spec-format.md` e apresente ao usuário o formato esperado para que ele o crie.

Se existir, leia `references/spec-format.md` para entender a sintaxe completa (incluindo modificadores de campo `[...]` e o tipo `paginated[NomeDoSchema]`) antes de interpretar o `SPEC.md` do usuário.

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

## Etapa 3 — Componentes Fixos

Leia `templates/fixed-components.yml` e copie os blocos aplicáveis para `components/`:

- `ErrorResponse` e `PaginationMeta` em `components/schemas` — **sempre**, mesmo que nenhum endpoint use paginação
- `securitySchemes` — conforme o tipo declarado em `## Security` no SPEC.md (`bearer_jwt`, `api_key` ou ambos)
- `RequestId` em `components/parameters` — **sempre**
- `PageParam`/`PageSizeParam` em `components/parameters` — apenas se algum endpoint usar `paginated[NomeDoSchema]`
- As 6 respostas de erro padrão em `components/responses` — **sempre**

---

## Etapa 4 — Schemas de Request/Response

Leia `references/type-mapping.md` (tipos e modificadores) e `templates/schema-patterns.md` (padrões de geração) e gere `components/schemas` para cada schema declarado em `## Schemas` no SPEC.md.

---

## Etapa 5 — Paths e Parâmetros

Leia `templates/paths-and-parameters.md` e aplique para cada endpoint: `operationId`, `X-Request-ID`, injeção automática de `PageParam`/`PageSizeParam` quando paginado, path/query/header params e `requestBody`.

---

## Etapa 6 — Respostas por Método HTTP

Leia `templates/responses-by-method.md` e gere as `responses` de cada endpoint conforme o método HTTP e o tipo de retorno declarado (`NomeDoSchema`, `list[NomeDoSchema]` ou `paginated[NomeDoSchema]`).

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

**Se o endpoint não declarar `security`**, pergunte ao usuário antes de assumir um valor.

---

## Etapa 8 — Onde Salvar

1. Verifique se `docs/openapi.yml` já existe.
   - **Se existir**, pergunte ao usuário se deseja **sobrescrever** o arquivo inteiro ou fazer **merge incremental** (mantendo paths/schemas existentes que não estão no SPEC.md atual e atualizando/adicionando apenas o que mudou). Não decida isso sozinho.
   - **Se não existir**, crie o diretório `docs/` se necessário e salve normalmente.

2. Após salvar, revise manualmente o arquivo gerado contra a lista em "Regras de Execução" abaixo antes de considerar a tarefa concluída.

---

## Etapa 9 — Gerar `.spectralrc.yml`

Após salvar `docs/openapi.yml` com sucesso, leia `templates/spectral-rules.md` e crie o arquivo `.spectralrc.yml` na raiz do projeto (mesmo nível de `SPEC.md`).

Esse arquivo deve conter **todas as regras de validação do [Spectral](https://github.com/stoplightio/spectral)** necessárias para confirmar que `docs/openapi.yml` respeita a estrutura e as convenções desta skill, entre elas:

- `operationId` único, em camelCase, no formato `{httpMethod}{PathSegments}`
- `X-Request-ID` referenciado via `$ref: '#/components/parameters/RequestId'` em todo endpoint
- Nenhum campo usando `nullable: true` (sintaxe OpenAPI 3.0)
- Respostas de erro padrão (400, 401, 403, 404, 422, 500) sempre via `$ref` para `components/responses`, nunca inline
- `examples` (plural) com chave `default` — nunca `example` (singular)
- Endpoints `GET`/`DELETE` sem `requestBody`
- `ErrorResponse` e `PaginationMeta` sempre presentes em `components/schemas`
- Os 6 erros padrão sempre presentes em `components/responses`
- `RequestId` sempre presente em `components/parameters`
- Endpoints com resposta paginada referenciando `PageParam` e `PageSizeParam`
- `security` declarado explicitamente em todo endpoint

Regras de aplicação:

1. Use exatamente o conteúdo de `templates/spectral-rules.md` como base — ele já cobre as validações acima com sintaxe válida do Spectral (`extends: spectral:oas` + regras customizadas).
2. Se `.spectralrc.yml` já existir na raiz do projeto, pergunte ao usuário se deseja **sobrescrever** ou **manter** o arquivo existente antes de continuar — não decida isso sozinho.
3. Após salvar, informe ao usuário o caminho do arquivo gerado (`.spectralrc.yml`) e como executar a validação: `npx @stoplight/spectral-cli lint docs/openapi.yml`.

---

## Regras de Execução

1. **Sempre leia o SPEC.md completo** antes de começar a gerar o YAML.
2. **Nunca escreva schemas ou respostas de erro inline** nos paths — sempre use `$ref: '#/components/schemas/{Nome}'` para schemas e `$ref: '#/components/responses/{Nome}'` para erros padrão.
3. **Sempre inclua `ErrorResponse` e `PaginationMeta`** em `components/schemas`, mesmo que o SPEC.md não declare ou não use paginação.
4. **Sempre inclua os códigos de resposta padrão** do método HTTP, mesmo que não declarados no SPEC.md.
5. **Se o endpoint não declarar `security`**, pergunte ao usuário antes de assumir.
6. **Se um schema referenciado em `responses` não estiver declarado em `## Schemas`**, avise o usuário e gere um schema vazio com comentário `# TODO: definir campos`.
7. **Nunca gere `nullable: true`** (sintaxe OpenAPI 3.0) — campos nullable usam `type: [tipo, "null"]`, conforme `references/type-mapping.md`.
8. **Nunca gere `requestBody` em endpoints `GET` ou `DELETE`** — se o SPEC.md declarar, avise o usuário.
9. **Endpoints com `paginated[NomeDoSchema]`** devem injetar `PageParam`/`PageSizeParam` e usar o formato `items` + `pagination` (`$ref: PaginationMeta`) — nunca criar um schema de wrapper nomeado por endpoint.
10. **Sempre valide manualmente se o YAML gerado é sintaticamente correto** antes de salvar — indentação e estrutura devem estar perfeitas.
11. **Se `docs/openapi.yml` já existir**, pergunte ao usuário antes de sobrescrever ou fazer merge.
12. **Sempre inclua `operationId`** em cada endpoint seguindo a convenção `{httpMethod}{PathSegments}` em camelCase — deve ser único em todo o arquivo.
13. **Sempre inclua `X-Request-ID`** em `components/parameters/RequestId` e referencie com `$ref: '#/components/parameters/RequestId'` como primeiro parâmetro de todos os endpoints.
14. **Sempre inclua os erros padrão em `components/responses`** e referencie-os via `$ref` — nunca inline. Use `examples` (plural) com chave `default` para todos os exemplos de request/response.
15. **Sempre gere `.spectralrc.yml`** na raiz do projeto logo após salvar `docs/openapi.yml`, conforme `templates/spectral-rules.md` — nunca pule essa etapa.
16. **Ao final**, informe ao usuário o caminho dos arquivos gerados (`docs/openapi.yml` e `.spectralrc.yml`) e a lista de endpoints documentados.
