import json
import math
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.municipio_repository import MunicipioRepository
from app.routing.base import RangeType
from app.routing.factory import get_provider


class LogisticsService:
    def __init__(self, db: AsyncSession):
        self.repo = MunicipioRepository(db)

    async def analyze(
        self,
        cities: list[str],
        max_travel_minutes: float | None = None,
        max_distance_km: float | None = None,
    ) -> dict:
        # 1. Resolve source cities from DB
        found = await self.repo.find_by_names(cities)
        not_found = [
            c for c in cities
            if MunicipioRepository._normalize(c)
            not in {MunicipioRepository._normalize(m["nome"]) for m in found}
        ]

        if not found:
            return self._empty(not_found)

        # 2. Determine routing constraint
        if max_travel_minutes:
            range_value = max_travel_minutes * 60   # seconds
            range_type  = RangeType.TIME
        else:
            range_value = max_distance_km * 1000    # metres
            range_type  = RangeType.DISTANCE

        # 3. Get isochrones from provider (raises EnvironmentError if no key)
        provider = get_provider()
        locations = [(float(m["longitude"]), float(m["latitude"])) for m in found]
        isochrones = await provider.get_isochrones(locations, range_value, range_type)

        # 4. Find municipalities within the union of isochrone polygons via PostGIS
        source_ids   = [m["id"] for m in found]
        polygon_jsons = [json.dumps(iso.geojson) for iso in isochrones]
        result = await self.repo.find_within_isochrone_union(polygon_jsons, source_ids)

        # 5. Enrich reachable cities with estimated travel metrics
        origin_cities = [
            {
                "codigo_ibge": m["codigo_ibge"],
                "nome": m["nome"],
                "uf": m["uf"],
                "latitude": float(m["latitude"]),
                "longitude": float(m["longitude"]),
                "populacao": m.get("populacao", 0) or 0,
            }
            for m in found
        ]

        reachable_cities = []
        total_dist = 0.0
        total_time = 0.0

        for c in result["cities"]:
            # Straight-line distance to closest origin (in km)
            sl_km = min(
                _haversine(float(m["latitude"]), float(m["longitude"]),
                           c["latitude"], c["longitude"])
                for m in found
            )
            # Road distance ≈ straight-line × 1.35 (typical road detour factor)
            est_dist = round(sl_km * 1.35, 1)
            # Avg road speed: 70 km/h
            est_time = round(est_dist / 70 * 60, 0)

            total_dist += est_dist
            total_time += est_time

            reachable_cities.append({
                "codigo_ibge": c["codigo_ibge"],
                "nome": c["nome"],
                "uf": c["uf"],
                "latitude": c["latitude"],
                "longitude": c["longitude"],
                "populacao": c.get("populacao", 0) or 0,
                "estimated_distance_km": est_dist,
                "estimated_time_minutes": int(est_time),
            })

        n = len(reachable_cities)
        total_pop = sum(c["populacao"] for c in reachable_cities)
        avg_dist  = round(total_dist / n, 1) if n else 0.0
        avg_time  = round(total_time / n, 0) if n else 0.0

        return {
            "origin_cities": origin_cities,
            "reachable_cities": reachable_cities,
            "total_population": total_pop,
            "cities_count": n,
            "avg_distance_km": avg_dist,
            "avg_time_minutes": int(avg_time),
            "isochrone_geojson": result["union_geojson"],
            "isochrone_area_km2": round(result["area_km2"], 2),
            "not_found": not_found,
        }

    @staticmethod
    def _empty(not_found):
        return {
            "origin_cities": [],
            "reachable_cities": [],
            "total_population": 0,
            "cities_count": 0,
            "avg_distance_km": 0.0,
            "avg_time_minutes": 0,
            "isochrone_geojson": None,
            "isochrone_area_km2": 0.0,
            "not_found": not_found,
        }


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Returns great-circle distance in km."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))
