import httpx
from fastapi import APIRouter, HTTPException, Query

from backend.schemas import Geocodificacao
from backend.services.nominatim import geocodificar


router = APIRouter(prefix="/api", tags=["Geocodificação"])


@router.get("/geocodificar", response_model=Geocodificacao)
async def buscar_coordenadas(
    q: str = Query(..., min_length=3, description="Cidade ou endereço a pesquisar"),
):
    try:
        resultado = await geocodificar(q)
    except httpx.TimeoutException:
        raise HTTPException(504, "O serviço de endereços demorou demais para responder. Tente novamente.")
    except httpx.HTTPStatusError:
        raise HTTPException(502, "O serviço de endereços retornou um erro. Tente novamente em instantes.")
    except httpx.RequestError:
        raise HTTPException(503, "Não foi possível conectar ao serviço de endereços.")

    if resultado is None:
        raise HTTPException(404, "Endereço não encontrado. Verifique e tente novamente.")

    return resultado