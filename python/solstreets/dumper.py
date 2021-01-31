from typing import Iterable, List
import logging
import ujson as json
from .entities import StreetSegment

logging.basicConfig(level="DEBUG")
log = logging.getLogger(__file__)


class StreetDumper:
    def __init__(self) -> None:
        super().__init__()

    def create_object(self, segments: Iterable[StreetSegment]) -> None:
        features = [
            {
                "geometry": {"type": "LineString", "coordinates": list(segment.points)},
                "type": "Feature",
                "properties": {
                    "name": segment.name,
                    "type": segment.type,
                    "slope": segment.slope,
                    "sun_diff": segment.sun_diff,
                    "length": segment.length,
                },
            }
            for segment in segments
        ]
        log.info(f"Creating {len(features)} features")
        return {"type": "FeatureCollection", "features": features}

    def dump(self, segments: Iterable[dict], out_file: str):
        segments_to_write = self.create_object(segments)
        log.info(f"Writing out segments to {out_file}")
        with open(out_file, "w") as f:
            json.dump(segments_to_write, f, indent=2)

    def dump_stats(self, stats_array: List[float], out_file: str):
        with open(out_file, "w") as f:
            json.dump(stats_array, f, indent=2)
            log.info(f"Wrote out stats to {out_file}")
