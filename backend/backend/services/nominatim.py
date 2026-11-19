import asyncio
import time

import httpx

from backend.schemas import Geocodificacao

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

HEADERS = {"User-Agent": "EcoMap/0.1 (projeto extensionista academico)"}

_trava = asyncio.Lock()
_ultima_requisicao = 0.0


async def _esperar_vez() -> None:
    global _ultima_requisicao
    async with _trava:
        espera = 1.0 - (time.monotonic() - _ultima_requisicao)
        if espera > 0:
            await asyncio.sleep(espera)

        _ultima_requisicao = time.monotonic()


async def geocodificar(endereco: str) -> Geocodificacao | None:
    await _esperar_vez()

    params = {
        "q": endereco,
        "format": "json",
        "limit": 1,
        "countrycodes": "br",
    }

    async with httpx.AsyncClient(timeout=30, headers=HEADERS) as client:
        resposta = await client.get(NOMINATIM_URL, params=params)
        resposta.raise_for_status()

    resultados = resposta.json()
    if not resultados:
        return None

    lugar = resultados[0]
    return Geocodificacao(
        lat=float(lugar["lat"]),
        lon=float(lugar["lon"]),
        endereco=lugar["display_name"],
    )
