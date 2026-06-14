from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


class RangeType(str, Enum):
    TIME = "time"
    DISTANCE = "distance"


@dataclass
class IsochroneResult:
    """Single isochrone polygon for one source location."""
    geojson: dict          # GeoJSON Polygon / MultiPolygon
    range_value: float     # seconds or metres
    range_type: RangeType


class IsochroneProvider(ABC):
    """Strategy interface for isochrone providers."""

    @abstractmethod
    async def get_isochrones(
        self,
        locations: list[tuple[float, float]],   # (lon, lat)
        range_value: float,                      # seconds or metres
        range_type: RangeType,
    ) -> list[IsochroneResult]:
        """Return one IsochroneResult per location."""
