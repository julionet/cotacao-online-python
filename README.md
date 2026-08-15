# Cotação Online API

API RESTful desenvolvida com **FastAPI** para consulta e gerenciamento de cotações financeiras em tempo real.

---

## Visão Geral

A aplicação expõe endpoints autenticados via JWT para:

- Registro e autenticação de usuários
- Listagem de pares de moedas disponíveis (integração com Airtable)
- Consulta de cotações financeiras em tempo real (integração com AwesomeAPI)
- Sincronização manual de cotações

---

## Tecnologias

| Pacote | Função |
|---|---|
| FastAPI | Framework web assíncrono |
| Uvicorn | Servidor ASGI |
| SQLAlchemy (async) | ORM e conexão com banco de dados |
| asyncpg | Driver PostgreSQL assíncrono |
| python-jose | Geração e validação de tokens JWT |
| passlib / bcrypt | Hash de senhas |
| httpx | Cliente HTTP assíncrono (integrações externas) |
| pydantic-settings | Gerenciamento de configurações via `.env` |

---

## Estrutura do Projeto

```
app/
├── core/           # Configurações, banco de dados, segurança e dependências
├── models/         # Modelos ORM (SQLAlchemy)
├── repositories/   # Camada de acesso a dados
├── routers/        # Definição de rotas (auth, currency, exchange)
├── schemas/        # Schemas de entrada e saída (Pydantic)
└── services/       # Regras de negócio e integrações externas
docs/               # Especificações, SQL e documentação OpenAPI
```

---

## Pré-requisitos

- Python 3.11+
- PostgreSQL
- Credenciais de acesso ao **Airtable** (tabelas `Currency` e `Exchange`)
- Credenciais de acesso à **AwesomeAPI** (cotações)

---

## Configuração

Crie um arquivo `.env` na raiz do projeto com as variáveis abaixo:

```env
# Banco de dados
DATABASE_URL=postgresql+asyncpg://usuario:senha@localhost:5432/cotacao_online

# JWT
SECRET_KEY=sua_chave_secreta_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# AwesomeAPI (cotações)
EXCHANGE_API_BASE_URL=https://economia.awesomeapi.com.br
EXCHANGE_API_TOKEN=
EXCHANGE_API_TIMEOUT=15

# Airtable (moedas)
AIRTABLE_BASE_URL=https://api.airtable.com/v0/<seu-base-id>
AIRTABLE_TOKEN=seu_token_airtable
AIRTABLE_TABLE_CURRENCY=Currency
AIRTABLE_TABLE_EXCHANGE=Exchange
AIRTABLE_TIMEOUT=30
```

### Banco de dados

Execute o script SQL para criar as tabelas necessárias:

```bash
psql -U usuario -d cotacao_online -f docs/create_tables.sql
```

---

## Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/cotacao-online-python.git
cd cotacao-online-python

# Crie e ative o ambiente virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux / macOS

# Instale as dependências
pip install -r requirements.txt
```

---

## Iniciando o Serviço

```bash
uvicorn app.main:app --reload
```

O serviço estará disponível em: **http://localhost:8000**

| Interface | URL |
|---|---|
| Documentação interativa (Swagger) | http://localhost:8000/docs |
| Documentação alternativa (ReDoc) | http://localhost:8000/redoc |

---

## Endpoints

### Auth — `/v1/auth`

| Método | Rota | Autenticação | Descrição |
|---|---|---|---|
| `POST` | `/v1/auth/register` | Pública | Registra novo usuário |
| `POST` | `/v1/auth/login` | Pública | Autentica o usuário e retorna tokens JWT |
| `POST` | `/v1/auth/refresh` | Bearer JWT | Renova o access token |
| `GET` | `/v1/auth/me` | Bearer JWT | Retorna dados do usuário autenticado |

### Currency — `/v1/currencies`

| Método | Rota | Autenticação | Descrição |
|---|---|---|---|
| `GET` | `/v1/currencies` | Bearer JWT | Lista os pares de moedas disponíveis |

### Exchange — `/v1/exchanges`

| Método | Rota | Autenticação | Descrição |
|---|---|---|---|
| `GET` | `/v1/exchanges` | Bearer JWT | Retorna as cotações das moedas ativas |
| `POST` | `/v1/exchanges/sync` | Bearer JWT | Sincroniza cotações com a API externa |

---

## Fluxo de Autenticação

```
1. POST /v1/auth/register  →  cria conta
2. POST /v1/auth/login     →  obtém access_token e refresh_token
3. GET  /v1/exchanges      →  envia Authorization: Bearer <access_token>
4. POST /v1/auth/refresh   →  renova o access_token com o refresh_token
```

---

## Licença

MIT — consulte [https://opensource.org/licenses/MIT](https://opensource.org/licenses/MIT)
