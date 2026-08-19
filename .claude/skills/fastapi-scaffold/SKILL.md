# Skill: Estruturar Projeto FastAPI do Zero

Você é responsável por criar a estrutura inicial completa de um projeto FastAPI. Siga as instruções abaixo com precisão.

Esta skill está dividida em vários arquivos. Leia cada um deles no momento indicado pela etapa correspondente — não é necessário carregar todos de uma vez.

```
.claude/skills/fastapi-scaffold/
├── SKILL.md                       (este arquivo — fluxo principal e regras de execução)
├── core/
│   └── infra-files.md             (main.py, config.py, database.py, security.py, validators.py, email.py, dependencies.py, limiter.py, logging.py, middleware.py)
├── auth/
│   ├── user-model.md              (models/base.py, models/user.py)
│   ├── auth-schemas.md            (schemas/pagination.py, schemas/user.py, schemas/auth.py)
│   ├── auth-repository.md         (repositories/base_repository.py, repositories/user_repository.py)
│   ├── auth-service.md            (services/auth_service.py)
│   └── auth-router.md             (routers/auth_router.py)
└── project-setup.md               (.env.example, .gitignore, requirements.txt)
```

## Como Invocar

O usuário deve fornecer:

**Opção A – Scaffold com entidade:**
```
projeto: {nome_do_projeto}
entidade: {NomeDaEntidade}
campos: {campo}: {tipo}, {campo}: {tipo}, ...
```

**Opção B – Scaffold vazio:**
```
projeto: {nome_do_projeto}
scaffold: vazio
```

## O Que Esta Skill Faz

### Para Opção A (com entidade):

1. Cria toda a estrutura de diretórios
2. Gera todos os arquivos base de `app/core/`
3. Gera `requirements.txt`, `.env.example` e `.gitignore`
4. Gera o modelo `User` completo com autenticação JWT e suporte a recuperação de senha
5. Gera o router `/auth` completo (`register`, `login`, `refresh`, `me`, `forgot-password`, `reset-password`) com rate limiting, montado sob `/api/v1`
6. Gera model, schema, repository, service e router para a entidade fornecida, também montado sob `/api/v1`
7. Configura inicialização automática do banco e tabelas no startup da aplicação

### Para Opção B (vazio):

1. Cria toda a estrutura de diretórios
2. Gera todos os arquivos base de `app/core/`
3. Gera `requirements.txt`, `.env.example` e `.gitignore`
4. Gera o modelo `User` completo com autenticação JWT e suporte a recuperação de senha
5. Gera o router `/auth` completo com rate limiting, montado sob `/api/v1`
6. **Não cria** nenhuma entidade adicional – projeto pronto para receber novas entidades
7. Configura inicialização automática do banco e tabelas no startup da aplicação

## Versionamento

Todos os endpoints de negócio (auth e entidades) são expostos sob o prefixo `/api/v1`. Esse prefixo é aplicado **apenas** em `app/main.py`, no `include_router(..., prefix="/api/v1")` — nunca dentro do `APIRouter(prefix=...)` de cada router individual, para manter os routers reutilizáveis caso a versão mude. O endpoint `/health` nunca é versionado.

## Estrutura de Diretórios a Criar

```
{project_name}/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   ├── validators.py
│   │   ├── email.py
│   │   ├── dependencies.py
│   │   ├── limiter.py
│   │   ├── logging.py
│   │   └── middleware.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── pagination.py
│   │   ├── user.py
│   │   └── auth.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base_repository.py
│   │   └── user_repository.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── auth_service.py
│   └── routers/
│       ├── __init__.py
│       └── auth_router.py
├── .env.example
├── .gitignore
└── requirements.txt
```

Para Opção A, adicionar dentro de `models/`, `schemas/`, `repositories/`, `services/` e `routers/` os arquivos da entidade fornecida.

## Etapa 1 — Arquivos de Infraestrutura (`app/core/`)

Leia `core/infra-files.md` e gere todos os arquivos de `app/core/`, incluindo `validators.py` e `email.py` (novos, usados pelo fluxo de recuperação de senha).

## Etapa 2 — Modelo de Usuário

Leia `auth/user-model.md` e gere `app/models/base.py` e `app/models/user.py`.

## Etapa 3 — Schemas de Autenticação

Leia `auth/auth-schemas.md` e gere `app/schemas/pagination.py`, `app/schemas/user.py` e `app/schemas/auth.py`.

## Etapa 4 — Repositórios

Leia `auth/auth-repository.md` e gere `app/repositories/base_repository.py` e `app/repositories/user_repository.py`.

## Etapa 5 — Serviço de Autenticação

Leia `auth/auth-service.md` e gere `app/services/auth_service.py`.

## Etapa 6 — Router de Autenticação

Leia `auth/auth-router.md` e gere `app/routers/auth_router.py`. Registre-o em `main.py` com `app.include_router(auth_router.router, prefix="/api/v1")`.

## Etapa 7 — Arquivos de Projeto

Leia `project-setup.md` e gere `.env.example`, `.gitignore` e `requirements.txt`.

## Etapa 8 (apenas Opção A) — Entidade Fornecida

Gere model, schema, repository, service e router para a entidade, seguindo o mesmo padrão estrutural de `auth/user-model.md` a `auth/auth-router.md` (sem os campos de senha/token, que são exclusivos de `User`). Registre o router em `main.py` também com `prefix="/api/v1"`.

## Regras de Execução

1. Crie **todos** os arquivos listados, incluindo os `__init__.py` vazios
2. Para Opção B, pare após criar os arquivos base – não crie entidade extra
3. Para Opção A, após criar os arquivos base, gere os 5 arquivos da entidade (model, schema, repository, service, router) e registre o router em `main.py` com `prefix="/api/v1"`
4. Ao gerar uma entidade, sempre herde de `TimestampedModel` em vez de `Base` — os campos `id`, `created_at` e `updated_at` são herdados automaticamente. Nunca repita esses campos no model da entidade
5. **Sempre importe todos os models concretos em `database.py`** antes de `init_db` ser chamado. `TimestampedModel` é abstrato e não precisa ser importado. Adicione os imports no topo do arquivo conforme os models existirem no projeto
6. O `lifespan` em `main.py` é o único lugar onde `init_db` é chamado — nunca chame em outro lugar
7. **Nunca crie o arquivo `.env`** – crie apenas `.env.example`. Se o projeto já existir e tiver um `.env`, não o sobrescreva
8. **Nunca sobrescreva um projeto existente** sem confirmar com o usuário. Se o diretório `{project_name}/` já existir, pergunte antes de prosseguir
9. Para endpoints de listagem, use `PaginationParams` como query parameter e retorne `PaginatedResponse[EntityResponse]`. Chame `BaseRepository.find_all(page, size)` no repositório e monte a resposta com `PaginatedResponse.build(...)`
10. Para novos routers de entidade, aplique `@limiter.limit("X/minute")` nos endpoints de escrita (`POST`, `PUT`, `PATCH`, `DELETE`) e inclua `request: Request` como primeiro parâmetro da função quando o decorator de limite estiver presente
11. O campo `password` nunca deve aparecer em nenhum schema de resposta
12. **Todos os routers (auth e entidades) são incluídos em `main.py` com `prefix="/api/v1"`** — nunca defina esse prefixo dentro do `APIRouter` de cada domínio, apenas no `include_router`. O endpoint `/health` nunca é versionado
13. O endpoint `POST /auth/refresh` recebe o refresh token **exclusivamente pelo header `refresh-token`** (nunca no body) e retorna `access_token` + `token_type`. Não recrie o schema `RefreshRequest`
14. O endpoint `POST /auth/forgot-password` gera um token numérico de 6 dígitos com `generate_reset_token()` (`app/core/security.py`), grava `reset_token` e `reset_token_expires` (`now + RESET_TOKEN_EXPIRE_MINUTES`) no usuário, envia por e-mail via `send_email()` (`app/core/email.py`) e retorna `{"token": "123456"}` com status 200. Se o e-mail não existir na base, retorna 404
15. O endpoint `PUT /auth/reset-password` exige `email`, `token` e `new_password` no body. Valida que o `token` confere com o `reset_token` armazenado e não expirou (senão 400), valida a força da nova senha, grava o hash, limpa `reset_token`/`reset_token_expires` e retorna 200 sem corpo de resposta
16. A validação de força de senha (mínimo 6 caracteres, 1 maiúscula, 1 minúscula, 1 número, 1 caractere não alfanumérico) vive em `app/core/validators.py::validate_password_strength` — reutilize essa função tanto em `UserCreate` quanto em `ResetPasswordRequest`; nunca duplique a regex
17. Sempre informe ao usuário quais arquivos foram criados ao final
