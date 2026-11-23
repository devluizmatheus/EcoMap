import asyncio

from backend.schemas import Material, PontoReciclagem
from backend.services import fontes
from backend.services.geoapify import converter_feature


def criar_feature(nome=None, lat=-7.17, lon=-34.81, raw=None):
    """Monta um lugar no formato da Geoapify, para os testes."""
    return {
        "properties": {
            "name": nome,
            "lat": lat,
            "lon": lon,
            "address_line2": "Avenida Brasil, João Pessoa - PB",
            "formatted": "Beco do Pancrácio, Varadouro, João Pessoa - PB",
            "place_id": "abc123",
            "datasource": {"raw": raw if raw is not None else {"osm_id": 1313089308}},
        }
    }


# ---------- converter_feature ----------

def test_converter_com_nome_usa_address_line2():
    ponto = converter_feature(criar_feature(nome="Centro de reciclagem"))
    assert ponto.nome == "Centro de reciclagem"
    assert ponto.endereco == "Avenida Brasil, João Pessoa - PB"


def test_converter_sem_nome_usa_endereco_completo():
    ponto = converter_feature(criar_feature(nome=None))
    assert ponto.nome is None
    assert ponto.endereco == "Beco do Pancrácio, Varadouro, João Pessoa - PB"


def test_converter_le_materiais_das_tags_do_osm():
    raw = {"osm_id": 1, "recycling:paper": "yes", "recycling:glass": "yes"}
    ponto = converter_feature(criar_feature(raw=raw))
    assert ponto.materiais == [Material.PAPEL, Material.VIDRO]


def test_converter_usa_place_id_quando_nao_tem_osm_id():
    ponto = converter_feature(criar_feature(raw={}))
    assert ponto.id == "abc123"


def test_converter_sem_coordenadas_devolve_none():
    feature = {"properties": {"name": "Sem lugar"}}
    assert converter_feature(feature) is None


# ---------- fontes.py: troca automática (RNF09) ----------

PONTO_OVERPASS = PontoReciclagem(id=1, lat=-7.1, lon=-34.8, materiais=[])
PONTO_GEOAPIFY = PontoReciclagem(id=2, lat=-7.2, lon=-34.9, materiais=[])


def test_fontes_usa_geoapify_quando_funciona(monkeypatch):
    async def geoapify_ok(lat, lon, raio):
        return [PONTO_GEOAPIFY]

    async def overpass_nao_deveria_rodar(lat, lon, raio):
        raise AssertionError("A Overpass não deveria ser chamada")

    monkeypatch.setattr(fontes, "buscar_pontos_geoapify", geoapify_ok)
    monkeypatch.setattr(fontes, "buscar_pontos_overpass", overpass_nao_deveria_rodar)

    resultado = asyncio.run(fontes.buscar_pontos(-7.1, -34.8, 2000))
    assert resultado == [PONTO_GEOAPIFY]


def test_fontes_usa_overpass_quando_geoapify_falha(monkeypatch):
    async def geoapify_com_erro(lat, lon, raio):
        raise RuntimeError("Geoapify fora do ar")

    async def overpass_ok(lat, lon, raio):
        return [PONTO_OVERPASS]

    monkeypatch.setattr(fontes, "buscar_pontos_geoapify", geoapify_com_erro)
    monkeypatch.setattr(fontes, "buscar_pontos_overpass", overpass_ok)

    resultado = asyncio.run(fontes.buscar_pontos(-7.1, -34.8, 2000))
    assert resultado == [PONTO_OVERPASS]