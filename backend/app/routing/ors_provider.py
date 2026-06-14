import httpx
from app.routing.base import IsochroneProvider, IsochroneResult, RangeType


ORS_BASE = "https://api.openrouteservice.org/v2"
TIMEOUT  = 30.0


class ORSProvider(IsochroneProvider):
    """OpenRouteService isochrone provider (driving-car profile)."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._headers = {
            "Authorization": api_key,
            "Content-Type": "application/json",
        }

    async def get_isochrones(
        self,
        locations: list[tuple[float, float]],
        range_value: float,
        range_type: RangeType,
    ) -> list[IsochroneResult]:
        payload = {
            "locations": [[lon, lat] for lon, lat in locations],
            "range": [range_value],
            "range_type": range_type.value,
            "attributes": ["area", "reachfactor"],
            "smoothing": 0.35,
        }

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.post(
                f"{ORS_BASE}/isochrones/driving-car",
                json=payload,
                headers=self._headers,
            )

        if resp.status_code == 401:
            raise ValueError("ORS API key inválida ou não autorizada.")
        if resp.status_code == 429:
            raise ValueError("Limite de requisições ORS atingido. Tente novamente mais tarde.")
        if not resp.is_success:
            detail = resp.text[:300]
            raise ValueError(f"ORS retornou status {resp.status_code}: {detail}")

        data = resp.json()
        features = data.get("features", [])

        results = []
        for feature in features:
            results.append(
                IsochroneResult(
                    geojson=feature["geometry"],
                    range_value=range_value,
                    range_type=range_type,
                )
            )
        return results
