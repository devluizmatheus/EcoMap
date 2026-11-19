from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers.pontos import router as pontos_router
from backend.routers.geocodificacao import router as geocodificacao_router


app = FastAPI(
    title="EcoMap API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET"],
    allow_headers=["*"]
)

app.include_router(pontos_router)
app.include_router(geocodificacao_router)


@app.get("/health", tags=["Status"])
async def health():
    return {"status": "ok"}
