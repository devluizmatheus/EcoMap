import httpx

from backend.schemas import Material, PontoReciclagem

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

HEADERS = {
    "User-Agent": "EcoMap/0.1 (projeto extensionista academico)",
}

TAGS_POR_MATERIAL: dict[Material, list[str]] = {
    Material.PAPEL: ["recycling:paper", "recycling:cardboard"],
    Material.PLASTICO: ["recycling:plastic", "recycling:plastic_bottles"],
    Material.VIDRO: ["recycling:glass", "recycling:glass_bottles"],
    Material.METAL: ["recycling:scrap_metal", "recycling:cans"],
    Material.ELETRONICO: ["recycling:electrical_items", "recycling:batteries"],
}


def montar_consulta(lat: float, lon: float, raio: int) -> str:
    return (
        "[out:json][timeout:25];"
        f'nwr["amenity"="recycling"](around:{raio},{lat},{lon});'
        "out center;"
    )


def extrair_materiais(tags: dict) -> list[Material]:
    materiais = []
    for material, chaves in TAGS_POR_MATERIAL.items():
        if any(tags.get(chave) == "yes" for chave in chaves):
            materiais.append(material)
    return materiais


def converter_elemento(elemento: dict) -> PontoReciclagem | None:
    if "lat" in elemento:
        lat, lon = elemento["lat"], elemento["lon"]
    elif "center" in elemento:
        lat, lon = elemento["center"]["lat"], elemento["center"]["lon"]
    else:
        return None

    tags = elemento.get("tags", {})
    return PontoReciclagem(
        id=elemento["id"],
        nome=tags.get("name"),
        endereco=tags.get("addr:street"),
        lat=lat,
        lon=lon,
        materiais=extrair_materiais(tags),
        horario=tags.get("opening_hours"),
    )


async def buscar_pontos(lat: float, lon: float, raio: int) -> list[PontoReciclagem]:
    consulta = montar_consulta(lat, lon, raio)

    async with httpx.AsyncClient(timeout=30, headers=HEADERS) as client:
        resposta = await client.post(OVERPASS_URL, data={"data": consulta})
        resposta.raise_for_status()

    elementos = resposta.json().get("elements", [])
    pontos = [converter_elemento(e) for e in elementos]
    return [p for p in pontos if p is not None]