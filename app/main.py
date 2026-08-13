from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import init_db
from app.routers import auth_router, currency_router, exchange_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Cotação Online API",
    version="1.0.0",
    description="API para consulta e gerenciamento de cotações financeiras",
    lifespan=lifespan,
)

app.include_router(auth_router.router)
app.include_router(currency_router.router)
app.include_router(exchange_router.router)
