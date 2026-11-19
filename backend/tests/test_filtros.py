from backend.schemas import Material, PontoReciclagem
from backend.services.filtros import distancia_metros, filtrar_por_materiais, ordenar_por_distancia


def criar_ponto(id, lat=0.0, lon=0.0, materiais=None):
    """Função auxiliar para criar pontos de teste com menos digitação."""
    return PontoReciclagem(id=id, lat=lat, lon=lon, materiais=materiais or [])


def test_filtro_sem_materiais_devolve_todos():
    pontos = [criar_ponto(1), criar_ponto(2)]
    assert filtrar_por_materiais(pontos, None) == pontos


def test_filtro_mantem_quem_aceita_pelo_menos_um():
    a = criar_ponto(1, materiais=[Material.VIDRO])
    b = criar_ponto(2, materiais=[Material.METAL])
    resultado = filtrar_por_materiais([a, b], [Material.VIDRO, Material.PAPEL])
    assert resultado == [a]


def test_filtro_descarta_ponto_sem_informacao():   # RN05
    sem_info = criar_ponto(1, materiais=[])
    assert filtrar_por_materiais([sem_info], [Material.VIDRO]) == []


def test_distancia_mesmo_ponto_e_zero():
    assert distancia_metros(-23.5, -46.6, -23.5, -46.6) == 0


def test_distancia_se_ao_masp():
    d = distancia_metros(-23.5503, -46.6339, -23.5614, -46.6559)
    assert 2500 < d < 2620   # cerca de 2,56 km


def test_ordenar_do_mais_perto_ao_mais_longe():
    longe = criar_ponto(1, lat=-23.60, lon=-46.65)
    perto = criar_ponto(2, lat=-23.561, lon=-46.65)
    resultado = ordenar_por_distancia([longe, perto], -23.56, -46.65)
    assert [p.id for p in resultado] == [2, 1]
    assert resultado[0].distancia_m < resultado[1].distancia_m