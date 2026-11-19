import logging

from backend.schemas import PontoReciclagem
from backend.services.geoapify import buscar_pontos_geoapify
from backend.services.overpass import buscar_pontos as buscar_pontos_overpass

logger = logging.getLogger("uvicorn.error")


async def buscar_pontos(lat: float, lon: float, raio: int) -> list[PontoReciclagem]:
    """Tenta a Geoapify; se falhar, usa a Overpass como reserva (RNF09)."""
    try:
        return await buscar_pontos_geoapify(lat, lon, raio)
    except Exception as erro:
        logger.warning("Geoapify falhou (%s). Tentando Overpass...", erro)
        return await buscar_pontos_overpass(lat, lon, raio)