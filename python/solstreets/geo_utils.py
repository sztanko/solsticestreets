from typing import Tuple
import math

EARTH_RADIUS = 6373000.0


def get_segment_length(segment: Tuple[Tuple[float, float], Tuple[float, float]]):

    lat1 = math.radians(segment[0][1])
    lon1 = math.radians(segment[0][0])
    lat2 = math.radians(segment[1][1])
    lon2 = math.radians(segment[1][0])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = (math.sin(dlat / 2)) ** 2 + math.cos(lat1) * math.cos(lat2) * (math.sin(dlon / 2)) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS * c


def get_segment_details(s: Tuple[Tuple[float, float], Tuple[float, float]]) -> Tuple[float, float]:
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