from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.coverage import router as coverage_router

app = FastAPI(
    title="Cobertura Territorial API",
    description="Análise de cobertura geográfica de municípios brasileiros",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(coverage_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
