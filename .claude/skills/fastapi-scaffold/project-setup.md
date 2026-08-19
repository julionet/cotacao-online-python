# Arquivos de Projeto

## `.env.example`

```
APP_NAME=Minha API
DEBUG=False
CORS_ORIGINS=["*"]
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
SECRET_KEY=sua-chave-secreta-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
RESET_TOKEN_EXPIRE_MINUTES=30
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=seu-usuario-smtp
SMTP_PASSWORD=sua-senha-smtp
SMTP_FROM=no-reply@example.com
```

## `.gitignore`

```
__pycache__/
*.pyc
*.pyo
*.pyd
.env
.venv/
venv/
*.egg-info/
dist/
build/
.pytest_cache/
.mypy_cache/
.ruff_cache/
```

## `requirements.txt`

```
fastapi>=0.111.0
uvicorn[standard]>=0.30.0
sqlalchemy[asyncio]>=2.0.0
asyncpg>=0.29.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
pydantic-settings>=2.0.0
pydantic[email]>=2.0.0
python-multipart>=0.0.9
slowapi>=0.1.9
httpx>=0.27.0
aiosmtplib>=3.0.0
```
