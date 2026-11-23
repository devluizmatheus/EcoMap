from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers.geocodificacao import router as geocodificacao_router
from backend.routers.pontos import router as pontos_router

load_dotenv()  # lê o .env e coloca as variáveis no ambiente

app = FastAPI(
    title="EcoMap API",
    description="API para localização de pontos de reciclagem",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(pontos_router)
app.include_router(geocodificacao_router)


@app.get("/health", tags=["Status"])
async def health():
    return {"status": "ok"}