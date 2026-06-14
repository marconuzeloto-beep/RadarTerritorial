from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, field_validator, model_validator
from app.database.connection import get_db
from app.services.coverage_service import CoverageService
from app.services.logistics_service import LogisticsService

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


# ── Polygon coverage ────────────────────────────────────────────────────────

class PolygonRequest(BaseModel):
    cities: list[str] = Field(..., min_length=1)
    buffer_km: float = Field(..., gt=0, le=2000)

    @field_validator("cities")
    @classmethod
    def cities_not_empty(cls, v):
        cleaned = [c.strip() for c in v if c.strip()]
        if not cleaned:
            raise ValueError("At least one city name is required.")
        return cleaned


class PolygonCoverageResponse(BaseModel):
    polygon_geojson: dict | None
    polygon_area_km2: float
    origin_cities: list[MunicipioOut]
    cities_found: list[MunicipioOut]
    not_found: list[str]


@router.post("/polygon", response_model=PolygonCoverageResponse)
async def analyze_polygon_coverage(
    payload: PolygonRequest, db: AsyncSession = Depends(get_db)
):
    service = CoverageService(db)
    try:
        result = await service.analyze_polygon(payload.cities, payload.buffer_km)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return result


# ── Logistics coverage ───────────────────────────────────────────────────────

def _clean_cities(v: list[str]) -> list[str]:
    cleaned = [c.strip() for c in v if c.strip()]
    if not cleaned:
        raise ValueError("At least one city name is required.")
    return cleaned


class LogisticsRequest(BaseModel):
    cities: list[str] = Field(..., min_length=1)
    max_travel_minutes: float | None = Field(default=None, gt=0, le=1440)
    max_distance_km: float | None   = Field(default=None, gt=0, le=5000)

    @field_validator("cities")
    @classmethod
    def cities_not_empty(cls, v):
        return _clean_cities(v)

    @model_validator(mode="after")
    def exactly_one_constraint(self):
        has_time = self.max_travel_minutes is not None
        has_dist = self.max_distance_km is not None
        if not has_time and not has_dist:
            raise ValueError(
                "Informe 'max_travel_minutes' ou 'max_distance_km'."
            )
        if has_time and has_dist:
            raise ValueError(
                "Informe apenas um critério: 'max_travel_minutes' ou 'max_distance_km'."
            )
        return self


class ReachableCityOut(BaseModel):
    codigo_ibge: str
    nome: str
    uf: str
    latitude: float
    longitude: float
    populacao: int
    estimated_distance_km: float
    estimated_time_minutes: int


class MunicipioWithPopOut(BaseModel):
    codigo_ibge: str
    nome: str
    uf: str
    latitude: float
    longitude: float
    populacao: int


class LogisticsResponse(BaseModel):
    origin_cities: list[MunicipioWithPopOut]
    reachable_cities: list[ReachableCityOut]
    total_population: int
    cities_count: int
    avg_distance_km: float
    avg_time_minutes: int
    isochrone_geojson: dict | None
    isochrone_area_km2: float
    not_found: list[str]


@router.post("/logistics", response_model=LogisticsResponse)
async def analyze_logistics_coverage(
    payload: LogisticsRequest, db: AsyncSession = Depends(get_db)
):
    service = LogisticsService(db)
    try:
        result = await service.analyze(
            cities=payload.cities,
            max_travel_minutes=payload.max_travel_minutes,
            max_distance_km=payload.max_distance_km,
        )
    except EnvironmentError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return result
