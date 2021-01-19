from typing import Generator, Iterable, Tuple, List
import math
import logging
from functools import lru_cache
from collections import Counter
from datetime import datetime
import ephem
from .entities import Street, StreetSegment, from_street
from .geo_utils import get_segment_details


logging.basicConfig(level="DEBUG")
log = logging.getLogger(__file__)


def combine_segments(street_segments: Iterable[StreetSegment]) -> Generator[StreetSegment, None, None]:
    previous_segment: StreetSegment = None
    c = 0
    c_combined = 0
    for segment in street_segments:
        c += 1
        if previous_segment:
            if previous_segment.points[1] == segment.points[0]:
                previous_segment.points[1] = segment.points[1]  # extend the segment
                previous_segment.length += segment.length  # and add up the length
                continue
            c_combined += 1
            yield previous_segment
        previous_segment = segment
    c_combined += 1
    yield previous_segment
    if c > 0:
        log.info(f"Processed {c} segments, combined them into {c_combined} ({c_combined*100/c:.2f} %)")


class AzimuthProcessor:
    def __init__(self, ts: datetime, threshold: float):
        self.ts = ts
        self.stats = Counter()
        self.threshold = threshold

    @lru_cache
    def get_sun_azimuth_cached(self, lng: float, lat: float) -> Tuple[float, float]:
        o = ephem.Observer()
        o.lat = str(lat)
        o.lon = str(lng)
        o.date = self.ts
        s = ephem.Sun()
        out = []
        for d in [o.next_rising(s), o.next_setting(s)]:
            o.date = d
            s.compute(o)
            az = math.degrees(s.az)
            if az > 180:
                az = az - 180
            log.info(f"Sunrise is on {d}, azimuth is {az}")
            out.append(az)
        return tuple(out)

    def get_sun_azimuth(self, lng: float, lat: float) -> Tuple[float, float]:
        return self.get_sun_azimuth_cached(round(lng, 0), round(lat, 0))

    def is_aligned_towards_sun(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> bool:
        seg_az = get_segment_details([p1, p2])[0]
        sun_az = self.get_sun_azimuth(p1[0], p1[1])
        # Count
        self.stats[round(seg_az)] += 1
        return abs(sun_az - seg_az) < self.threshold

    def add_alignment_data(self, street_segment: StreetSegment) -> StreetSegment:
        p1, p2 = street_segment.points
        seg_az, length = get_segment_details([p1, p2])
        sun_az = self.get_sun_azimuth(p1[0], p1[1])
        # Count
        self.stats[round(seg_az)] += length
        street_segment.slope = seg_az
        street_segment.sun_diff = min(abs(az - seg_az) for az in sun_az)
        street_segment.length = length
        return street_segment

    def process_segments(self, street: Street) -> Generator[StreetSegment, None, None]:
        previous_point = None
        for point in street.points:
            if previous_point:
                segment = from_street(street, previous_point, point)
                self.add_alignment_data(segment)
                yield segment
            previous_point = point

    def get_stats(self) -> List[int]:
        return [self.stats.get(i, 0) for i in range(0, 180)]
