from typing import Tuple, List, Generator
import math
from shapely.geometry import box
from shapely.geometry.point import Point as P

EARTH_RADIUS = 6373000.0
Point = Tuple[float, float]
PointTuple = Tuple[Point, Point]


def get_segment_length(segment: PointTuple):

    lat1 = math.radians(segment[0][1])
    lon1 = math.radians(segment[0][0])
    lat2 = math.radians(segment[1][1])
    lon2 = math.radians(segment[1][0])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = (math.sin(dlat / 2)) ** 2 + math.cos(lat1) * math.cos(lat2) * (math.sin(dlon / 2)) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS * c


def get_bb_area(bbox: PointTuple) -> float:
    origin = bbox[0]
    x = (bbox[0][0], bbox[1][1])
    y = (bbox[1][0], bbox[0][1])
    x_length = get_segment_length((origin, x))
    y_length = get_segment_length((origin, y))
    area = x_length * y_length / (1000 * 1000)
    return area


def get_bb(boxes: List[PointTuple]) -> PointTuple:
    p1 = [180, 90]
    p2 = [-180, -90]
    for box in boxes:
        if box[0][0] < p1[0]:
            p1[0] = box[0][0]
        if box[0][1] < p1[1]:
            p1[1] = box[0][1]
        if box[1][0] > p2[0]:
            p2[0] = box[1][0]
        if box[1][1] > p2[1]:
            p2[1] = box[1][1]
    return (tuple(p1), tuple(p2))


def subdivide_bb(bb: PointTuple, subdivide_factor: int) -> Generator[PointTuple, None, None]:
    w = (bb[1][0] - bb[0][0]) / subdivide_factor
    h = (bb[1][1] - bb[0][1]) / subdivide_factor
    for i in range(0, subdivide_factor):
        for j in range(0, subdivide_factor):
            p1 = (bb[0][0] + i * w, bb[0][1] + j * h)
            p2 = (bb[0][0] + (i + 1) * w, bb[0][1] + (j + 1) * h)
            yield (p1, p2)


def bb_intersects(bb1: PointTuple, bb2: PointTuple):
    """ bb2 - city"""
    sh_bb1 = box(bb1[0][0], bb1[0][1], bb1[1][0], bb1[1][1])
    sh_bb2 = P(bb2[0])  # We are checking the bottom left corner only
    return sh_bb1.touches(sh_bb2) or sh_bb1.contains(sh_bb2)


def get_segment_details(s: PointTuple) -> Tuple[float, float]:
    p = (s[0][0], s[1][1])
    dy = get_segment_length((s[0], p))
    dx = get_segment_length((p, s[1]))
    if s[0][0] > s[1][0]:
        dx = -dx
    if s[0][1] > s[1][1]:
        dy = -dy
    az = math.degrees(math.atan2(dy, dx))
    if az < 0:
        az = az + 180
    az = (-az + 270) % 360
    if az > 180:
        az = az - 180
    return az, get_segment_length(s)