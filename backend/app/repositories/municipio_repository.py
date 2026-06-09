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
                CAST(latitude AS FLOAT) AS latitude,
                CAST(longitude AS FLOAT) AS longitude
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

    @staticmethod
    def _normalize(name: str) -> str:
        import unicodedata
        nfkd = unicodedata.normalize("NFKD", name.lower().strip())
        return "".join(c for c in nfkd if not unicodedata.combining(c))
