from shapely.geometry import shape
import fiona
import sys
from utils.filtersfuncs import *
from utils.geomutils import combineSegments
import json


def getSegments(coords, matchF):
    segments = []
    for i in range(0, len(coords) - 1):
        segment = (coords[i], coords[i + 1])
        if matchF(segment):
            segments.append(segment)
    return segments


# inp = "zip://%s" %(sys.argv[1])
inp = sys.argv[1]
outp = sys.argv[2]
jsonp = sys.argv[3]
print("In: %s, out: %s, json: %s" % (inp, outp, jsonp))


def filt(name):
    out = []
    c = fiona.open("roads.shp", "r")
    for g in c:
        if g["properties"]["name"] == name:
            out.append(g)
    return out


allowedTypes = set(
    "pedestrian,living_street,bridleway,road,trunk,unclassified,path,steps,primary,secondary,tertiary,service,residential".split(
        ","
    )
)


def propFilter(props):
    if props["tunnel"] != 0:
        return False
    if props["type"] not in allowedTypes:
        return False
    return True


schema = {
    "geometry": "LineString",
    "properties": {"name": "str", "length": "int", "azimuth_d": "float"},
}
sun_az = 0.0
with fiona.open(inp, "r") as source:
    with fiona.open(outp, "w", crs=source.crs, driver=source.driver, schema=schema) as target:
        for g in source:
            if not propFilter(g["properties"]):
                continue

            coords = g["geometry"]["coordinates"]
            name = g["properties"]["name"]
            segments = getSegments(coords, combinedFilter)
            segments = combineSegments(segments)
            for s in segments:
                sun_az = getSunAzimuth(s[0])
                str_az = getSegmentAzimuth(s)
                l = int(getLength(s))
                if l < 120:
                    continue
                az_diff = int(100.0 * abs(sun_az - str_az)) / 100.0
                geom = {"type": "LineString", "coordinates": s}
                shape = {
                    "geometry": geom,
                    "type": "Feature",
                    "properties": {"name": name, "length": l, "azimuth_d": az_diff},
                }
                target.write(shape)

sl = stats["solsticeLength"]
tl = stats["totalLength"]
h = [int(v) for v in stats["hist"]]

print(
    "Total length: %d, solstice length: %d, expected value: %d, anomaly: %d%%, sun azimuth: %f"
    % (tl, sl, 6 * tl / 180, 100 * sl / (6 * tl / 180), sun_az)
)

stats = {
    "totalLength": tl,
    "solsticeLength": sl,
    "sun_azimuth": sun_az,
    "ratio": int(10000 * sl / tl),
    "hist": h,
}

with open(jsonp, "w") as outfile:
    json.dump(stats, outfile)