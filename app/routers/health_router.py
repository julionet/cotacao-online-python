from typing import Optional

from fastapi import APIRouter, Header, status

router = APIRouter(prefix="/v1", tags=["Health"])


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    responses={
        400: {"description": "Requisição inválida"},
        404: {"description": "Recurso não encontrado"},
        500: {"description": "Erro interno do servidor"},
    },
)
async def health(x_request_id: Optional[str] = Header(None, alias="X-Request-Id")):
    """Verifica se a API está funcionando."""
    return {"status": "ok"}
