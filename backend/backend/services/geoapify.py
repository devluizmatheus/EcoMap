import os

import httpx

from backend.schemas import PontoReciclagem
from backend.services.overpass import extrair_materiais

GEOAPIFY_URL = "https://api.geoapify.com/v2/places"


def converter_feature(feature: dict) -> PontoReciclagem | None:
    """Transforma um lugar da Geoapify em PontoReciclagem."""
    props = feature.get("properties", {})
    lat, lon = props.get("lat"), props.get("lon")
    if lat is None or lon is None:
        return None

    # Tags originais do OpenStreetMap (onde ficam os recycling:*)
    tags = props.get("datasource", {}).get("raw", {})
    nome = props.get("name")

    return PontoReciclagem(
        id=tags.get("osm_id") or props.get("place_id"),
        nome=nome,
        # com nome: address_line2 já é o endereço; sem nome: usa o endereço completo
        endereco=props.get("address_line2") if nome else props.get("formatted"),
        lat=lat,
        lon=lon,
        materiais=extrair_materiais(tags),
        horario=tags.get("opening_hours"),
    )


async def buscar_pontos_geoapify(lat: float, lon: float, raio: int) -> list[PontoReciclagem]:
    chave = os.getenv("GEOAPIFY_API_KEY")
    if not chave:
        raise RuntimeError("GEOAPIFY_API_KEY não configurada no .env")

    params = {
        "categories": "service.recycling",
        "filter": f"circle:{lon},{lat},{raio}",   # longitude primeiro!
        "bias": f"proximity:{lon},{lat}",
        "limit": 100,
        "apiKey": chave,
    }

    async with httpx.AsyncClient(timeout=15) as client:
        resposta = await client.get(GEOAPIFY_URL, params=params)
        resposta.raise_for_status()

    pontos = [converter_feature(f) for f in resposta.json().get("features", [])]
    return [p for p in pontos if p is not None]