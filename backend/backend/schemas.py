from enum import Enum
from pydantic import BaseModel, Field


class Material(str, Enum):
    PAPEL = "papel"
    PLASTICO = "plastico"
    VIDRO = "vidro"
    METAL = "metal"
    ELETRONICO = "eletronico"


class Coordenadas(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lon: float = Field(..., ge=-180, le=180, description="Longitude")


class Geocodificacao(Coordenadas):
    endereco: str = Field(..., description="Endereço encontrado pelo Nominatim")


class PontoReciclagem(BaseModel):
    id: int | str = Field(..., description="Identificador do ponto (OSM ou Geoapify)")
    nome: str | None = None
    endereco: str | None = None
    lat: float
    lon: float
    materiais: list[Material] = []
    horario: str | None = None
    distancia_m: float | None = Field(None, description="Distância até a busca, em metros")


class RespostaPontos(BaseModel):
    centro: Coordenadas
    raio_m: int
    total: int
    pontos: list[PontoReciclagem]
