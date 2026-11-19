from backend.schemas import Material
from backend.services.overpass import converter_elemento, extrair_materiais, montar_consulta


def test_montar_consulta_inclui_coordenadas_e_raio():
    consulta = montar_consulta(-23.56, -46.65, 2000)
    assert "around:2000,-23.56,-46.65" in consulta
    assert '"amenity"="recycling"' in consulta


def test_extrair_materiais_reconhece_tags_com_yes():
    tags = {"recycling:paper": "yes", "recycling:glass_bottles": "yes"}
    assert extrair_materiais(tags) == [Material.PAPEL, Material.VIDRO]


def test_extrair_materiais_reconhece_cada_material():
    tags = {
        "recycling:paper": "yes",
        "recycling:plastic": "yes",
        "recycling:glass": "yes",
        "recycling:scrap_metal": "yes",
        "recycling:electrical_items": "yes",
    }
    assert extrair_materiais(tags) == list(Material)


def test_extrair_materiais_ignora_tags_com_no():
    tags = {"recycling:paper": "no"}
    assert extrair_materiais(tags) == []


def test_converter_node_usa_lat_lon_direto():
    elemento = {"type": "node", "id": 1, "lat": -23.5, "lon": -46.6, "tags": {"name": "Ecoponto A"}}
    ponto = converter_elemento(elemento)
    assert ponto.lat == -23.5
    assert ponto.nome == "Ecoponto A"


def test_converter_way_usa_center():
    elemento = {"type": "way", "id": 2, "center": {"lat": -23.7, "lon": -46.8}, "tags": {}}
    ponto = converter_elemento(elemento)
    assert ponto.lat == -23.7
    assert ponto.nome is None   # RN04: sem nome continua válido


def test_converter_sem_coordenadas_devolve_none():
    elemento = {"type": "relation", "id": 3, "tags": {}}
    assert converter_elemento(elemento) is None