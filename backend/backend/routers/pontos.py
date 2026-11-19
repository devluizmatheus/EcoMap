import httpx
from fastapi import APIRouter, HTTPException, Query

from backend.schemas import Coordenadas, Material, RespostaPontos
from backend.services.filtros import filtrar_por_materiais, ordenar_por_distancia
from backend.services.fontes import buscar_pontos

router = APIRouter(prefix="/api", tags=["Pontos de reciclagem"])


@router.get("/pontos", response_model=RespostaPontos)
async def listar_pontos(
    lat: float = Query(..., ge=-90, le=90, description="..."),
    lon: float = Query(..., ge=-180, le=180, description="..."),
    raio: int = Query(2000, ge=100, le=10000, description="..."),
    materiais: list[Material] | None = Query(None, description="..."),
):
    try:
        pontos = await buscar_pontos(lat, lon, raio)
    except httpx.TimeoutException:
        raise HTTPException(504, "O serviço de mapas demorou demais ara responder. Tente novamente")
    except httpx.HTTPStatusError as erro:
        print("Overpass respondeu:", erro.response.status_code)
        print(erro.response.text[:500])
        raise HTTPException(502, "O serviço de mapas retornou um erro. Tente novamente em instantes.")
    except httpx.RequestError:
        raise HTTPException(503, "Não foi possível conectar ao serviço de mapas.")

    pontos = filtrar_por_materiais(pontos, materiais)
    pontos = ordenar_por_distancia(pontos, lat, lon)

    return RespostaPontos(
        centro=Coordenadas(lat=lat, lon=lon),
        raio_m=raio,
        total=len(pontos),
        pontos=pontos,
    )


@router.get("/materiais", response_model=list[Material])
async def listar_materiais():
    return list(Material)

