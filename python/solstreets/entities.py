from typing import Tuple, List
from dataclasses import dataclass
from shapely.geometry import LineString
from shapely.geometry.base import BaseGeometry


@dataclass
class Street:
    """Class for keeping track of an item in inventory."""

    name: str
    type: str
    points: List[Tuple[float, float]]


@dataclass
class StreetSegment(Street):
    slope: float
    sun_diff: float
    length: float


def from_street(street: Street, p1: Tuple[float, float], p2: Tuple[float, float]) -> StreetSegment:
    return StreetSegment(name=street.name, type=street.type, points=[p1, p2], slope=0, sun_diff=0, length=0)
