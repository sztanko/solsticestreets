from typing import Tuple, Optional
import logging
import time
import typer
import json
import re
from pathlib import Path
from collections import Counter
from solstreets.geo_utils import get_bb_area, get_segment_details, get_segment_length

logging.basicConfig(level="DEBUG")
log = logging.getLogger(__file__)

from geopy.geocoders import Nominatim

AGENT_NAME = "Solstice streets/1.0"
DELAY = 1
JSON_INDENT = 2

MAX_AREA_SQKM = 10000

# time cat config/cities_small.json | jq  '[.[] |  {"name": .Name, "country": .Country}] | sort_by(.name)'


app = typer.Typer()


def normalize_name(s: str) -> str:
    # Remove all non-word characters (everything except numbers and letters)
    s = re.sub(r"[^\w\s]", "", s)

    # Replace all runs of whitespace with a single dash
    s = re.sub(r"\s+", "_", s)
    return s


def get_bb(geolocator: Nominatim, lookup_str: str) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    log.info(f"Looking up {lookup_str}")
    response = geolocator.geocode(lookup_str)
    if not response:
        raise Exception(f"Couldn't lookup {lookup_str}")
    bb = response.raw["boundingbox"]
    bb = [float(b) for b in bb]
    bbox = ((bb[2], bb[0]), (bb[3], bb[1]))
    log.info(f"Returned {bbox}")
    log.info(f"Sleeping the system for {DELAY} seconds")
    time.sleep(DELAY)
    return bbox


def get_bb_city(geolocator: Nominatim, city: str, country: str) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    lookup = {"city": city, "country": country}
    log.info(f"Looking up {lookup}")
    response = geolocator.geocode(lookup)
    if not response:
        raise Exception(f"Couldn't lookup {lookup}")
    bb = response.raw["boundingbox"]
    bb = [float(b) for b in bb]
    bbox = ((bb[2], bb[0]), (bb[3], bb[1]))
    log.info(f"Returned {bbox}")
    log.info(f"Sleeping the system for {DELAY} seconds")
    time.sleep(DELAY)
    return bbox


def get_add_key(city: dict) -> str:
    key = normalize_name(f"{city['name']}__{city['country']}")
    return key.lower()


def enforce_float_coordinates(city: dict):
    b = city["bb"]
    city["bb"] = ((float(b[0][0]), float(b[0][1])), (float(b[1][0]), float(b[1][1])))
    return city


def dedup_cities(cities: list) -> list:
    out = []
    city_set = set()
    for city in cities:
        k = (city["name"], city["country"])
        if k not in city_set:
            city_set.add(k)
            out.append(city)
    return out


def enrich(city_list: list, ignore_failed_cities: bool = False, lookup_large_areas: bool = False) -> Tuple[list, dict]:
    geolocator = Nominatim(user_agent=AGENT_NAME)
    log.info(f"Loaded {len(city_list)} cities")
    out = []
    stats = Counter()
    stats["in_count"] = len(city_list)
    city_list = dedup_cities(city_list)
    failed_cities = set()
    stats["dedup_count"] = len(city_list)
    stats["errors"] = 0
    for d in city_list:
        city_success = True
        try:
            if "key" not in d:
                d["key"] = get_add_key(d)
                stats["add_key"] += 1
            if "bb" not in d or (get_bb_area(d["bb"]) > MAX_AREA_SQKM and lookup_large_areas):
                d["bb"] = get_bb_city(geolocator, d["name"], d["country"])
                stats["bb_lookup"] += 1
            d = enforce_float_coordinates(d)
            if d["bb"]:
                area = get_bb_area(d["bb"])
                d["area"] = int(area)
                stats["total_area"] += area
                if area > MAX_AREA_SQKM:
                    log.warning(f"Area for {d['name']}, {d['country']} is {int(area)} sq km, that is too large")
                    stats["area_too_large"] += 1
        except Exception as e:
            log.error(f"Couldn't enrich {d}")
            stats["errors"] += 1
            log.exception(e)
            failed_cities.add(d["key"])
            if ignore_failed_cities:
                city_success = False
                log.warn("Removing the city from config")
        if city_success:
            out.append(d)
    out.sort(key=lambda d: (d["name"], d["country"]))
    log.warning(f"Failed enrichined these cities: {', '.join(list(failed_cities))}")
    if ignore_failed_cities:
        log.warning("Because you asked to remove failed cities, removing them from the list")
    return out, dict(stats)


@app.command(help="Add bounding box, deduplicate, etc")
def enrich_cities(
    config_file: str, ignore_failed: bool = typer.Option(False), lookup_large_areas: bool = typer.Option(False)
):
    log.info("You can get bounding boxes using this tool: http://norbertrenner.de/osm/bbox.html")
    with open(config_file, "r") as f:
        cities, stats = enrich(json.load(f), ignore_failed, lookup_large_areas)
    log.info("Stats:")
    for k, c in stats.items():
        log.info(f"{k}:\t{c}")
    with open(config_file, "w") as f:
        json.dump(cities, f, indent=JSON_INDENT)
        log.info(f"Wrote {len(cities)} back")


@app.command(help="Print the geojson for the bounding boxes of all ")
def get_cities_geojson(config_file: str):
    features = []
    with open(config_file, "r") as f:
        cities = json.load(f)
        for city in cities:
            [[x0, y0], [x1, y1]] = city["bb"]
            rect = [[x0, y0], [x0, y1], [x1, y1], [x1, y0], [x0, y0]]
            feature = {
                "type": "Feature",
                "properties": {
                    "name": city["name"],
                    "country": city["country"],
                    "key": city["key"],
                    "area": city["area"],
                },
                "geometry": {"type": "Polygon", "coordinates": [rect]},
            }
            features.append(feature)

    out = {"type": "FeatureCollection", "features": features}
    print(json.dumps(out, indent=2))


@app.command(help="Geocode a location and show it's bounding box")
def geocode(city: str = typer.Argument("City to geocode"), country: str = typer.Argument("Country to geocode")):
    geolocator = Nominatim(user_agent=AGENT_NAME)
    try:
        b = get_bb_city(geolocator, city, country)
        area = get_bb_area(b)
        url = f"https://linestrings.com/bbox/#{b[0][0]},{b[0][1]},{b[1][0]},{b[1][1]}"
        print(f"Area is {int(area):,} sq km")
        print(url)
    except:
        print(f"Couldn't geocode {location}, sorry")


@app.command(help="Generate Osmium config file for extrction")
def generate_osmium_config(
    config_file: str = typer.Argument(..., help="Input config json file"),
    extract_dir: str = typer.Argument(..., help="Destination directory of extracts"),
    osmium_config_file: str = typer.Argument(..., help="Where to write the file"),
):
    out = {"directory": extract_dir}
    enrich_cities(config_file)
    with open(config_file, "r") as f:
        cities = json.load(f)
        extracts = []
        for city in cities[0:10]:
            bb = city["bb"]
            extract = {
                "output": f"{city['key']}.osm.pbf",
                "output_header": {"generator": AGENT_NAME},
                "bbox": [bb[0][0], bb[0][1], bb[1][0], bb[1][1]],
            }
            extracts.append(extract)
    out["extracts"] = extracts
    with open(osmium_config_file, "w") as f:
        json.dump(out, f, indent=JSON_INDENT)
        Path(extract_dir).mkdir(parents=True, exist_ok=True)
        log.info(f"Wrote osmium config to {osmium_config_file}. Also created {extract_dir}, if didn't exist")
        log.info(
            f"Run the command with:\nosmium extract -O -c {osmium_config_file} --strategy=simple  planet-latest.osm.pbf"
        )


if __name__ == "__main__":
    app()