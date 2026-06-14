import json
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.municipio_repository import MunicipioRepository


class CoverageService:
    def __init__(self, db: AsyncSession):
        self.repo = MunicipioRepository(db)

    async def analyze(self, cities: list[str], radius_km: float) -> dict:
        found = await self.repo.find_by_names(cities)

        not_found = []
        found_names_normalized = {
            MunicipioRepository._normalize(m["nome"]) for m in found
        }
        for city in cities:
            if MunicipioRepository._normalize(city) not in found_names_normalized:
                not_found.append(city)

        if not found:
            return {
                "covered_cities": [],
                "discovered_cities": [],
                "not_found": not_found,
                "analyzed_count": 0,
                "discovered_count": 0,
            }

        source_ids = [m["id"] for m in found]
        discovered_raw = await self.repo.find_all_within_radius_of_set(source_ids, radius_km)

        covered_cities = [
            {
                "codigo_ibge": m["codigo_ibge"],
                "nome": m["nome"],
                "uf": m["uf"],
                "latitude": m["latitude"],
                "longitude": m["longitude"],
            }
            for m in found
        ]

        discovered_cities = [
            {
                "codigo_ibge": m["codigo_ibge"],
                "nome": m["nome"],
                "uf": m["uf"],
                "latitude": m["latitude"],
                "longitude": m["longitude"],
                "distance_km": round(float(m["distance_km"]), 1),
            }
            for m in discovered_raw
        ]

        return {
            "covered_cities": covered_cities,
            "discovered_cities": discovered_cities,
            "not_found": not_found,
            "analyzed_count": len(covered_cities),
            "discovered_count": len(discovered_cities),
        }

    async def analyze_polygon(self, cities: list[str], buffer_km: float) -> dict:
        found = await self.repo.find_by_names(cities)

        not_found = []
        found_names_normalized = {
            MunicipioRepository._normalize(m["nome"]) for m in found
        }
        for city in cities:
            if MunicipioRepository._normalize(city) not in found_names_normalized:
                not_found.append(city)

        if not found:
            return {
                "polygon_geojson": None,
                "polygon_area_km2": 0.0,
                "origin_cities": [],
                "cities_found": [],
                "not_found": not_found,
            }

        source_ids = [m["id"] for m in found]
        data = await self.repo.build_polygon_and_find_cities(source_ids, buffer_km)

        origin_cities = [
            {
                "codigo_ibge": m["codigo_ibge"],
                "nome": m["nome"],
                "uf": m["uf"],
                "latitude": float(m["latitude"]),
                "longitude": float(m["longitude"]),
            }
            for m in found
        ]

        cities_found = [
            {
                "codigo_ibge": c["codigo_ibge"],
                "nome": c["nome"],
                "uf": c["uf"],
                "latitude": float(c["latitude"]),
                "longitude": float(c["longitude"]),
            }
            for c in data["cities"]
        ]

        polygon_geojson = json.loads(data["polygon_geojson"]) if data["polygon_geojson"] else None

        return {
            "polygon_geojson": polygon_geojson,
            "polygon_area_km2": round(data["area_km2"], 2),
            "origin_cities": origin_cities,
            "cities_found": cities_found,
            "not_found": not_found,
        }
