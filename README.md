# 🌿 EcoMap

Aplicação web para encontrar **pontos de reciclagem próximos**, com mapa interativo, busca por endereço ou localização atual e filtro por tipo de material.

O backend em **FastAPI** integra três serviços de dados geográficos (Geoapify, OpenStreetMap/Overpass e Nominatim), com troca automática de fonte em caso de falha. O frontend em **React + Leaflet** é responsivo e pode ser instalado no celular como aplicativo (PWA).

## ✨ Funcionalidades

- **Busca por endereço ou bairro**, convertendo o texto em coordenadas (geocodificação)
- **Localização atual** pelo GPS do dispositivo
- **Filtro por material**: papel, plástico, vidro, metal e eletrônicos
- **Escolha da distância máxima** (2, 5 ou 10 km), com sugestão para ampliar a busca quando não há resultados
- **Mapa interativo** com alfinetes numerados, do ponto mais próximo ao mais distante
- **Lista de resultados** ligada ao mapa: ao tocar num ponto, o mapa se move até ele
- **"Como chegar"**: abre a rota até o ponto no Google Maps
- **Layout responsivo**, com painel recolhível no celular
- **Instalável como aplicativo (PWA)**, com ícone na tela inicial


## 🛠️ Tecnologias

| Camada | Tecnologias |
|---|---|
| **Backend** | Python 3.14, FastAPI, Pydantic, HTTPX (assíncrono), Poetry |
| **Frontend** | React, Vite, Leaflet / React Leaflet, vite-plugin-pwa |
| **Dados geográficos** | Geoapify Places API, Overpass API (OpenStreetMap), Nominatim |
| **Testes** | Pytest, pytest-cov |
| **Infraestrutura** | Docker, Docker Compose, Nginx |


## 🚀 Como rodar

### Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) e Docker Compose
- Uma chave gratuita da [Geoapify](https://www.geoapify.com/)

### Configuração

Copie o arquivo de exemplo e preencha a sua chave da Geoapify:

```bash
cp backend/.env.example backend/.env
```

```
GEOAPIFY_API_KEY=sua_chave_aqui
```

### Com Docker (recomendado)

```bash
docker compose up --build
```

Acesse **http://localhost:8080**. A documentação interativa da API (Swagger) fica em **http://localhost:8080/docs**.

---

## 🔌 Endpoints da API

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/api/pontos?lat=&lon=&raio=&materiais=` | Busca pontos de reciclagem próximos, filtrados e ordenados por distância |
| `GET` | `/api/geocodificar?q=` | Converte um endereço em coordenadas |
| `GET` | `/api/materiais` | Lista os materiais disponíveis para filtro |
| `GET` | `/health` | Verifica se a API está em funcionamento |


## 📁 Estrutura do projeto

```
EcoMap/
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── .env.example
│   ├── backend/
│   │   ├── main.py
│   │   ├── schemas.py
│   │   ├── routers/
│   │   │   ├── pontos.py
│   │   │   └── geocodificacao.py
│   │   └── services/
│   │       ├── fontes.py
│   │       ├── geoapify.py
│   │       ├── overpass.py
│   │       ├── nominatim.py
│   │       └── filtros.py
│   └── tests/
└── frontend/
    ├── Dockerfile
    ├── nginx.conf
    ├── vite.config.js
    ├── public/            (ícones do PWA)
    └── src/
        ├── App.jsx
        ├── materiais.js
        ├── services/api.js
        └── components/
            ├── Busca.jsx
            ├── Filtros.jsx
            ├── SeletorRaio.jsx
            └── ListaPontos.jsx
```

## 📜 Dados e créditos

- Dados de mapas e pontos de reciclagem: © [colaboradores do OpenStreetMap](https://www.openstreetmap.org/copyright), disponíveis sob a licença ODbL
- Busca de locais: [Geoapify](https://www.geoapify.com/)
- Geocodificação: [Nominatim](https://nominatim.org/)

A disponibilidade de pontos varia conforme a região, de acordo com o que está cadastrado no OpenStreetMap.