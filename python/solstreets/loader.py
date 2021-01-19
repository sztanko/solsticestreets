from typing import List, Generator
from dataclasses import dataclass
import logging
from .entities import Street
import ujson as json

logging.basicConfig(level="DEBUG")
log = logging.getLogger(__file__)

TYPE = "LineString"
AVAILABLE_HIGHWAYS = set(
    [
        "bridleway",
        "living_street",
        "path",
        "pedestrian",
        "primary",
        "residential",
        "road",
        "secondary",
        "service",
        "steps",
        "tertiary",
        "trunk",
        "unclassified",
    ]
)
EXCLUDED_HIGHWAYS = set(["abandoned"])
EXCLUDED_TAGS = ["tunnel", "proposed", "construction"]
ROAD_TAG = "highway"
ID_TAG = "id"
GEOMETRY_COLUMN = "geometry"


class OSMLoader:
    def __init__(self):
        pass

    def filter_tags(self, tags: dict) -> bool:
        return (
            ROAD_TAG in tags
            and tags[ROAD_TAG] in AVAILABLE_HIGHWAYS
            and not any(t in tags for t in EXCLUDED_TAGS)
            and tags[ROAD_TAG] not in EXCLUDED_HIGHWAYS
        )

    def convert(self, obj: dict) -> Street:
        g = obj[GEOMETRY_COLUMN]
        tags = obj.get("properties", {})
        points = g.get("coordinates", [])
        return Street(
            name=tags.get("name"),
            type=tags.get(ROAD_TAG),
            points=points,
        )

    def read(self, input_file: str, road_types: List[str] = AVAILABLE_HIGHWAYS) -> Generator[Street, None, None]:
        c = 0
        c_filtered = 0
        for line in open(input_file, "r"):
            obj = json.loads(line)
            g = obj[GEOMETRY_COLUMN]
            tags = obj.get("properties", {})
            c += 1
            if g["type"] == TYPE and self.filter_tags(tags) and g.get("coordinates", []):
                c_filtered += 1
                yield self.convert(obj)
        log.info(f"Loaded {c} ways, filtered down to {c_filtered} streets")
