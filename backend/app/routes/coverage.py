from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, field_validator
from app.database.connection import get_db
from app.services.coverage_service import CoverageService

router = APIRouter(prefix="/coverage", tags=["coverage"])


class CoverageRequest(BaseModel):
    cities: list[str] = Field(..., min_length=1)
    radius_km: float = Field(..., gt=0, le=5000)

    @field_validator("cities")
    @classmethod
    def cities_not_empty(cls, v):
        cleaned = [c.strip() for c in v if c.strip()]
        if not cleaned:
            raise ValueError("At least one city name is required.")
        return cleaned


class MunicipioOut(BaseModel):
    codigo_ibge: str
    nome: str
    uf: str
    latitude: float
    longitude: float


class MunicipioDiscoveredOut(MunicipioOut):
    distance_km: float


class CoverageResponse(BaseModel):
    covered_cities: list[MunicipioOut]
    discovered_cities: list[MunicipioDiscoveredOut]
    not_found: list[str]
    analyzed_count: int
    discovered_count: int


@router.post("/radius", response_model=CoverageResponse)
async def analyze_coverage(payload: CoverageRequest, db: AsyncSession = Depends(get_db)):
    service = CoverageService(db)
    try:
        result = await service.analyze(payload.cities, payload.radius_km)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return result
