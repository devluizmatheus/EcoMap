from math import asin, cos, radians, sin, sqrt

from backend.schemas import Material, PontoReciclagem


RAIO_TERRA_M = 6_371_000

def filtrar_por_materiais(
    pontos: list[PontoReciclagem],
    materiais: list[Material] | None,
) -> list[PontoReciclagem]:

    if not materiais:
        return pontos

    return [
        ponto for ponto in pontos
        if any(m in ponto.materiais for m in materiais)
    ]

    
def distancia_metros(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    # Fórmula de Haversine
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * RAIO_TERRA_M * asin(sqrt(a))


def ordenar_por_distancia(pontos: list[PontoReciclagem], lat: float, lon: float) -> list[PontoReciclagem]:
    for ponto in pontos:
        ponto.distancia_m = round(distancia_metros(lat, lon, ponto.lat, ponto.lon), 1)
    return sorted(pontos, key=lambda p: p.distancia_m)

