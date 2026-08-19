# Skill: Criar Novo Endpoint FastAPI

Você é responsável por adicionar uma nova entidade completa a um projeto FastAPI já estruturado (pelo scaffold). Siga as instruções abaixo com precisão.

Esta skill está dividida em vários arquivos. Leia cada um deles no momento indicado pela etapa correspondente — não é necessário carregar todos de uma vez.

```
.claude/skills/fastapi-endpoint/
├── SKILL.md                (este arquivo — fluxo principal e regras de execução)
├── entity-model.md          (model + mapeamento de tipos)
├── entity-schema.md         (schemas Create/Update/Response)
├── entity-repository.md     (repository, incl. find_by_{field} para campos unique)
├── entity-service.md        (service, incl. validação de unicidade em create/update)
├── entity-router.md         (router HTTP)
└── registration.md          (registro em main.py e database.py)
```

## Como Invocar

O usuário deve fornecer:

```
entidade: {NomeDaEntidade}
campos: {campo}: {tipo}, {campo}: {tipo} unique, ...
métodos: GET, POST, PUT, DELETE  (informar apenas os desejados)
```

O modificador opcional `unique` após o tipo marca o campo como único: o model recebe `unique=True, index=True`, o repository ganha um `find_by_{campo}`, e o service passa a validar duplicidade (`409 Conflict`) em `create`/`update` para esse campo.

**Exemplo:**
```
entidade: Product
campos: name: str, sku: str unique, price: float, description: str, is_available: bool
métodos: GET, POST, PUT, DELETE
```

## O Que Esta Skill Faz

1. Cria `app/models/{entity}.py` — modelo SQLAlchemy herdando de `TimestampedModel`
2. Cria `app/schemas/{entity}.py` — schemas Pydantic (Create, Update, Response com timestamps)
3. Cria `app/repositories/{entity}_repository.py` — repositório herdando de `BaseRepository`, com `find_by_{field}` para cada campo `unique`
4. Cria `app/services/{entity}_service.py` — lógica de negócio com paginação e validação de unicidade para campos `unique`
5. Cria `app/routers/{entity}_router.py` — endpoints HTTP com paginação e rate limiting
6. Registra o router em `app/main.py` sob o prefixo `/api/v1`
7. Adiciona import do model em `app/core/database.py`

## Etapa 1 — Model

Leia `entity-model.md` e gere `app/models/{entity}.py`, incluindo `unique=True, index=True` nos campos marcados como `unique`.

## Etapa 2 — Schema

Leia `entity-schema.md` e gere `app/schemas/{entity}.py`.

## Etapa 3 — Repository

Leia `entity-repository.md` e gere `app/repositories/{entity}_repository.py`, incluindo um `find_by_{field}` para cada campo `unique`.

## Etapa 4 — Service

Leia `entity-service.md` e gere `app/services/{entity}_service.py`, incluindo a validação de unicidade em `create`/`update` para cada campo `unique`.

## Etapa 5 — Router

Leia `entity-router.md` e gere `app/routers/{entity}_router.py` com os endpoints correspondentes aos métodos HTTP solicitados.

## Etapa 6 — Registro no Projeto

Leia `registration.md` e registre o router em `main.py` (com `prefix="/api/v1"`) e o import do model em `database.py`.

## Regras de Execução

1. Antes de criar qualquer arquivo, verifique se `app/main.py` existe — se não existir, informe o usuário que o projeto precisa ser scaffoldado primeiro com o agente `fastapi-scaffold`
2. Sempre herde de `TimestampedModel` — **nunca** de `Base`. Os campos `id`, `created_at` e `updated_at` são herdados automaticamente; não os declare no model
3. Sempre herde o repository de `BaseRepository[{Entity}]` — não reimplemente `find_by_id`, `find_all`, `create`, `update` e `delete` se já existem na classe pai
4. Sempre use paginação no endpoint de listagem (`GET /`) com `PaginationParams` e `PaginatedResponse`
5. Aplique `@limiter.limit("30/minute")` e inclua `request: Request` nos endpoints de escrita: `POST`, `PUT`, `DELETE`
6. O schema `Response` sempre inclui `id: uuid.UUID`, `created_at: datetime` e `updated_at: datetime`
7. Gere **apenas** os métodos do repository, service e router que correspondem aos métodos HTTP solicitados pelo usuário
8. Nunca omita os `__init__.py` — verifique se existem antes de criar os arquivos
9. Sempre use `model_dump(exclude_unset=True)` no update para suportar atualização parcial
10. Sempre adicione o import do novo model em `app/core/database.py` para garantir que a tabela seja criada no startup
11. O campo `password` nunca deve aparecer em nenhum schema de resposta
12. O router da entidade é registrado em `main.py` com `prefix="/api/v1"` — nunca declare esse prefixo no `APIRouter` do próprio router
13. **Para cada campo marcado com o modificador `unique`** na invocação: adicione `unique=True, index=True` na coluna do model, um método `find_by_{field}` no repository, e a validação de duplicidade (`409 Conflict`) em `create` e `update` no service. Campos sem esse modificador não recebem nenhuma dessas validações
14. No `update`, a validação de unicidade só roda se o campo `unique` estiver presente no payload **e** o valor for diferente do atual — nunca dispare `409` quando o cliente reenviar o mesmo valor já existente na entidade
15. Se o usuário fornecer tipos inválidos ou ambíguos (ex.: `list`, `dict`, `any`), pergunte antes de assumir um tipo
16. Sempre informe ao usuário a lista de arquivos criados/modificados, os endpoints disponíveis (com o prefixo `/api/v1`) e quais campos têm validação de unicidade ativa, ao final
