from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


class MunicipioRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_names(self, names: list[str]) -> list[dict]:
        """Find municipalities by exact or normalized name match."""
        placeholders = ", ".join(f":name{i}" for i in range(len(names)))
        params = {f"name{i}": name for i, name in enumerate(names)}

        query = text(f"""
            SELECT
                id,
                codigo_ibge,
                nome,
                uf,
                CAST(latitude AS FLOAT)  AS latitude,
                CAST(longitude AS FLOAT) AS longitude,
                COALESCE(populacao, 0)   AS populacao
            FROM municipios
            WHERE unaccent(lower(nome)) IN ({placeholders})
        """)

        normalized = [self._normalize(n) for n in names]
        params = {f"name{i}": normalized[i] for i in range(len(normalized))}

        result = await self.db.execute(query, params)
        return [dict(row._mapping) for row in result.fetchall()]

    async def find_within_radius(
        self, source_ids: list[int], radius_km: float, exclude_ids: list[int]
    ) -> list[dict]:
        """
        Find all municipalities within radius_km of ANY of the source municipalities.
        Uses ST_DWithin on geography type for accurate metre-based distance.
        Excludes the source municipalities themselves.
        """
        source_placeholder = ", ".join(str(i) for i in source_ids)
        exclude_placeholder = ", ".join(str(i) for i in exclude_ids) if exclude_ids else "0"

        query = text(f"""
            SELECT DISTINCT ON (m.id)
                m.id,
                m.codigo_ibge,
                m.nome,
                m.uf,
                CAST(m.latitude AS FLOAT) AS latitude,
                CAST(m.longitude AS FLOAT) AS longitude,
                CAST(
                    MIN(
                        ST_Distance(
                            m.geom::geography,
                            src.geom::geography
                        )
                    ) OVER (PARTITION BY m.id) / 1000.0
                AS FLOAT) AS distance_km
            FROM municipios m
            CROSS JOIN (
                SELECT geom FROM municipios WHERE id IN ({source_placeholder})
            ) src
            WHERE
                m.id NOT IN ({exclude_placeholder})
                AND ST_DWithin(
                    m.geom::geography,
                    src.geom::geography,
                    :radius_m
                )
            ORDER BY m.id, distance_km
        """)

        result = await self.db.execute(query, {"radius_m": radius_km * 1000})
        return [dict(row._mapping) for row in result.fetchall()]

    async def find_all_within_radius_of_set(
        self, source_ids: list[int], radius_km: float
    ) -> list[dict]:
        """
        Finds all municipalities within radius_km of ANY source municipality,
        returning closest distance. Excludes source municipalities.
        """
        source_placeholder = ", ".join(str(i) for i in source_ids)

        query = text(f"""
            WITH source_geoms AS (
                SELECT geom FROM municipios WHERE id IN ({source_placeholder})
            ),
            candidates AS (
                SELECT
                    m.id,
                    m.codigo_ibge,
                    m.nome,
                    m.uf,
                    CAST(m.latitude AS FLOAT) AS latitude,
                    CAST(m.longitude AS FLOAT) AS longitude,
                    MIN(
                        ST_Distance(m.geom::geography, sg.geom::geography)
                    ) / 1000.0 AS distance_km
                FROM municipios m
                CROSS JOIN source_geoms sg
                WHERE ST_DWithin(m.geom::geography, sg.geom::geography, :radius_m)
                  AND m.id NOT IN ({source_placeholder})
                GROUP BY m.id, m.codigo_ibge, m.nome, m.uf, m.latitude, m.longitude
            )
            SELECT * FROM candidates ORDER BY distance_km, nome
        """)

        result = await self.db.execute(query, {"radius_m": radius_km * 1000})
        return [dict(row._mapping) for row in result.fetchall()]

    async def find_within_isochrone_union(
        self, polygon_geojsons: list[str], exclude_ids: list[int]
    ) -> dict:
        """
        Receives a list of GeoJSON polygon strings (one per source city isochrone),
        unions them with ST_Union, then finds all municipalities inside via ST_Within.
        All spatial operations run entirely in PostGIS.
        """
        # Build UNION ALL CTE for all polygon strings
        union_parts = "\n    UNION ALL\n    ".join(
            f"SELECT ST_GeomFromGeoJSON(:{f'poly{i}'}) AS geom"
            for i in range(len(polygon_geojsons))
        )
        params = {f"poly{i}": g for i, g in enumerate(polygon_geojsons)}

        exclude_clause = ", ".join(str(i) for i in exclude_ids) if exclude_ids else "0"

        query = text(f"""
            WITH input_polys AS (
                {union_parts}
            ),
            unioned AS (
                SELECT ST_Union(geom) AS geom FROM input_polys
            )
            SELECT
                ST_AsGeoJSON(u.geom)                       AS union_geojson,
                ST_Area(u.geom::geography) / 1e6           AS area_km2,
                m.id,
                m.codigo_ibge,
                m.nome,
                m.uf,
                CAST(m.latitude  AS FLOAT)                 AS latitude,
                CAST(m.longitude AS FLOAT)                 AS longitude,
                COALESCE(m.populacao, 0)                   AS populacao
            FROM unioned u
            JOIN municipios m ON ST_Within(m.geom, u.geom)
            WHERE m.id NOT IN ({exclude_clause})
            ORDER BY m.nome
        """)

        result = await self.db.execute(query, params)
        rows = result.fetchall()

        if not rows:
            # Polygon exists but no cities inside — still return the polygon shape
            union_gjson, area = await self._get_isochrone_union_only(polygon_geojsons)
            return {"union_geojson": union_gjson, "area_km2": area, "cities": []}

        import json
        union_geojson = json.loads(rows[0]._mapping["union_geojson"])
        area_km2      = float(rows[0]._mapping["area_km2"])
        cities = [
            {
                "id":           r._mapping["id"],
                "codigo_ibge":  r._mapping["codigo_ibge"],
                "nome":         r._mapping["nome"],
                "uf":           r._mapping["uf"],
                "latitude":     r._mapping["latitude"],
                "longitude":    r._mapping["longitude"],
                "populacao":    r._mapping["populacao"],
            }
            for r in rows
        ]
        return {"union_geojson": union_geojson, "area_km2": area_km2, "cities": cities}

    async def _get_isochrone_union_only(self, polygon_geojsons: list[str]) -> tuple:
        union_parts = "\n    UNION ALL\n    ".join(
            f"SELECT ST_GeomFromGeoJSON(:{f'poly{i}'}) AS geom"
            for i in range(len(polygon_geojsons))
        )
        params = {f"poly{i}": g for i, g in enumerate(polygon_geojsons)}
        query = text(f"""
            WITH input_polys AS ({union_parts}),
            unioned AS (SELECT ST_Union(geom) AS geom FROM input_polys)
            SELECT
                ST_AsGeoJSON(geom)             AS union_geojson,
                ST_Area(geom::geography) / 1e6 AS area_km2
            FROM unioned
        """)
        result = await self.db.execute(query, params)
        row = result.fetchone()
        if row:
            import json
            return json.loads(row._mapping["union_geojson"]), float(row._mapping["area_km2"])
        return None, 0.0

    async def build_polygon_and_find_cities(
        self, source_ids: list[int], buffer_km: float
    ) -> dict:
        """
        Builds a convex hull around source city points, expands it by buffer_km,
        then finds all municipalities inside that polygon.
        All spatial operations run in PostGIS.
        Returns polygon GeoJSON, area in km², and matching city rows.
        """
        source_placeholder = ", ".join(str(i) for i in source_ids)

        query = text(f"""
            WITH source_points AS (
                SELECT geom FROM municipios WHERE id IN ({source_placeholder})
            ),
            hull AS (
                SELECT ST_ConvexHull(ST_Collect(geom)) AS geom FROM source_points
            ),
            buffered AS (
                SELECT
                    ST_Buffer(geom::geography, :buffer_m)::geometry AS geom
                FROM hull
            )
            SELECT
                ST_AsGeoJSON(b.geom)                              AS polygon_geojson,
                ST_Area(b.geom::geography) / 1e6                 AS area_km2,
                m.id,
                m.codigo_ibge,
                m.nome,
                m.uf,
                CAST(m.latitude  AS FLOAT)                       AS latitude,
                CAST(m.longitude AS FLOAT)                       AS longitude
            FROM buffered b
            JOIN municipios m
              ON ST_Within(m.geom, b.geom)
             AND m.id NOT IN ({source_placeholder})
            ORDER BY m.nome
        """)

        result = await self.db.execute(query, {"buffer_m": buffer_km * 1000})
        rows = result.fetchall()

        if not rows:
            # Still need polygon even if no cities found
            polygon_geojson, area_km2 = await self._get_polygon_only(source_ids, buffer_km)
            return {"polygon_geojson": polygon_geojson, "area_km2": area_km2, "cities": []}

        polygon_geojson = rows[0]._mapping["polygon_geojson"]
        area_km2 = float(rows[0]._mapping["area_km2"])
        cities = [
            {
                "id": r._mapping["id"],
                "codigo_ibge": r._mapping["codigo_ibge"],
                "nome": r._mapping["nome"],
                "uf": r._mapping["uf"],
                "latitude": r._mapping["latitude"],
                "longitude": r._mapping["longitude"],
            }
            for r in rows
        ]
        return {"polygon_geojson": polygon_geojson, "area_km2": area_km2, "cities": cities}

    async def _get_polygon_only(self, source_ids: list[int], buffer_km: float) -> tuple:
        source_placeholder = ", ".join(str(i) for i in source_ids)
        query = text(f"""
            WITH hull AS (
                SELECT ST_ConvexHull(ST_Collect(geom)) AS geom
                FROM municipios WHERE id IN ({source_placeholder})
            )
            SELECT
                ST_AsGeoJSON(ST_Buffer(geom::geography, :buffer_m)::geometry) AS polygon_geojson,
                ST_Area(ST_Buffer(geom::geography, :buffer_m)) / 1e6          AS area_km2
            FROM hull
        """)
        result = await self.db.execute(query, {"buffer_m": buffer_km * 1000})
        row = result.fetchone()
        if row:
            return row._mapping["polygon_geojson"], float(row._mapping["area_km2"])
        return None, 0.0

    @staticmethod
    def _normalize(name: str) -> str:
        import unicodedata
        nfkd = unicodedata.normalize("NFKD", name.lower().strip())
        return "".join(c for c in nfkd if not unicodedata.combining(c))
