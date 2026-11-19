import httpx
from fastapi.testclient import TestClient

from backend.main import app
from backend.schemas import Geocodificacao, Material, PontoReciclagem

client = TestClient(app)

# ⚠️ Use o nome da sua pasta de rotas: "routers" ou "routes"
ROTA_PONTOS = "backend.routers.pontos"
ROTA_GEO = "backend.routers.geocodificacao"


def test_health():
    resposta = client.get("/health")
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_materiais_lista_os_cinco():
    resposta = client.get("/api/materiais")
    assert resposta.json() == ["papel", "plastico", "vidro", "metal", "eletronico"]


def test_pontos_filtra_e_ordena(monkeypatch):
    async def buscar_falso(lat, lon, raio):
        return [
            PontoReciclagem(id=1, lat=-23.60, lon=-46.65, materiais=[Material.VIDRO]),
            PontoReciclagem(id=2, lat=-23.561, lon=-46.65, materiais=[Material.VIDRO]),
            PontoReciclagem(id=3, lat=-23.562, lon=-46.65, materiais=[Material.METAL]),
        ]

    monkeypatch.setattr(f"{ROTA_PONTOS}.buscar_pontos", buscar_falso)

    resposta = client.get("/api/pontos", params={"lat": -23.56, "lon": -46.65, "materiais": "vidro"})
    dados = resposta.json()

    assert resposta.status_code == 200
    assert dados["total"] == 2                          # o ponto 3 (metal) foi filtrado
    assert [p["id"] for p in dados["pontos"]] == [2, 1]  # ordenado por distância


def test_pontos_sem_resultado_nao_e_erro(monkeypatch):   # RN06
    async def buscar_vazio(lat, lon, raio):
        return []

    monkeypatch.setattr(f"{ROTA_PONTOS}.buscar_pontos", buscar_vazio)

    resposta = client.get("/api/pontos", params={"lat": -23.56, "lon": -46.65})
    assert resposta.status_code == 200
    assert resposta.json()["total"] == 0


def test_pontos_latitude_invalida():
    resposta = client.get("/api/pontos", params={"lat": 200, "lon": -46.65})
    assert resposta.status_code == 422


def test_pontos_overpass_fora_do_ar(monkeypatch):
    async def buscar_com_erro(lat, lon, raio):
        raise httpx.ConnectError("sem conexão")

    monkeypatch.setattr(f"{ROTA_PONTOS}.buscar_pontos", buscar_com_erro)

    resposta = client.get("/api/pontos", params={"lat": -23.56, "lon": -46.65})
    assert resposta.status_code == 503


def test_geocodificar_encontra(monkeypatch):
    async def geo_falso(endereco):
        return Geocodificacao(lat=-23.56, lon=-46.65, endereco="Av. Paulista, São Paulo")

    monkeypatch.setattr(f"{ROTA_GEO}.geocodificar", geo_falso)

    resposta = client.get("/api/geocodificar", params={"q": "Av. Paulista"})
    assert resposta.status_code == 200
    assert resposta.json()["lat"] == -23.56


def test_geocodificar_nao_encontra(monkeypatch):
    async def geo_vazio(endereco):
        return None

    monkeypatch.setattr(f"{ROTA_GEO}.geocodificar", geo_vazio)

    resposta = client.get("/api/geocodificar", params={"q": "xyzxyz"})
    assert resposta.status_code == 404