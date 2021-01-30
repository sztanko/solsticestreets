from typing import Tuple, List, Generator
import logging
import json
from pathlib import Path
from solstreets.constants import CITY_FOLDER, JSON_INDENT, AGENT_NAME, OSMIUM_CONFIG_FOLDER, CITY_FOLDER, SUFFIX
from solstreets.geo_utils import PointTuple, bb_intersects, get_bb, subdivide_bb

logging.basicConfig(level="INFO")
log = logging.getLogger(__file__)


def get_bb_for(bb: PointTuple, cities: List[dict]) -> Tuple[PointTuple, List[dict]]:
    out: List[dict] = []
    for city in cities:
        b = city["bb"]
        if bb_intersects(bb, b):
            out.append(city)
    big_bb = get_bb([c["bb"] for c in out])
    return (big_bb, out)


class SpaceSplitter:
    def __init__(
        self,
        cities: List[dict],
        input_osm_file: str,
        output_path: str,
        split_factor: int,
        max_cities: int,
    ) -> None:
        self.cities = cities
        self.input_osm_file = input_osm_file
        self.output_path = output_path
        self.osmium_config_path = output_path + "/" + OSMIUM_CONFIG_FOLDER
        self.city_path = output_path + "/" + CITY_FOLDER
        self.configs: List[Tuple[int, dict, int]] = []
        self._seq_id = 0
        self.split_factor = split_factor
        self.max_cities = max_cities
        Path(self.osmium_config_path).mkdir(parents=True, exist_ok=True)
        Path(self.city_path).mkdir(parents=True, exist_ok=True)

    def generate_config(self, input_osm: str, items: List[Tuple[PointTuple, str]]) -> dict:
        out = {"directory": self.city_path}
        extracts = []
        for item in items:
            bb = item[0]
            extract = {
                "output": f"{item[1]}",
                "output_header": {"generator": AGENT_NAME},
                "bbox": [bb[0][0], bb[0][1], bb[1][0], bb[1][1]],
            }
            extracts.append(extract)
        out["extracts"] = extracts
        return out

    def generate_artifacts(self) -> None:
        features = []
        cmd_lines = []
        for parent_seq, config, seq in self.configs:
            osmium_config_location = f"{self.osmium_config_path}/region_{parent_seq:04}.osmium.json"
            with open(osmium_config_location, "w") as f:
                json.dump(config, f, indent=JSON_INDENT)
            input_file = self.get_input_osm_name(parent_seq)
            if parent_seq > 0:
                input_file = f"{self.city_path}/{input_file}"
            cmd = f"time osmium extract --overwrite --strategy=simple -c {osmium_config_location} {input_file}"
            cmd_lines.append(cmd)
            for box in config["extracts"]:
                # log.info(box)
                [x0, y0, x1, y1] = box["bbox"]
                rect = [[x0, y0], [x0, y1], [x1, y1], [x1, y0], [x0, y0]]
                feature = {
                    "type": "Feature",
                    "properties": {
                        "output": box["output"],
                        "seq": seq,
                        "parent_seq": parent_seq,
                        "parent_seq_file": self.get_input_osm_name(parent_seq),
                    },
                    "geometry": {"type": "Polygon", "coordinates": [rect]},
                }
                features.append(feature)
        out = {"type": "FeatureCollection", "features": features}
        log.info("Generated %d features from %d configs", len(features), len(self.configs))
        cmd_lines.sort()
        with open(f"{self.output_path}/tree.geojson", "w") as fw:
            log.info("Writing geojson")
            json.dump(out, fw)
        bash_file = self.output_path + "/run.sh"
        with open(bash_file, "w") as f:
            log.info(f"Writing {bash_file}")
            for step, line in enumerate(cmd_lines, 1):
                f.write(f"echo 'Step {step} out of {len(cmd_lines)}'\n")
                f.write(line)
                f.write("\n")
            f.write("echo 'Removing intermediate files'\n")
            f.write(f"rm {self.city_path}/region_*{SUFFIX}\n")
            f.write("echo 'Done'\n")

    def get_input_osm_name(self, seq_number) -> str:
        if seq_number == 0:
            return self.input_osm_file
        return f"region_{seq_number:04}{SUFFIX}"

    def subdivide(self, bb: PointTuple, cities: List[dict], parent_seq: int, level: int = 0) -> None:
        # This method generates a config and a command line for procesing
        log.debug("Parent %d, subdivision at level %d", parent_seq, level)
        input_osm_name = self.get_input_osm_name(parent_seq)
        log.debug("Dealing with %d cities", len(cities))
        if len(cities) <= self.max_cities:
            items = [(city["bb"], f"{city['key']}{SUFFIX}") for city in cities]
            config = self.generate_config(input_osm_name, items)
            self.configs.append((parent_seq, config, self._seq_id))
            return
        log.debug("Subdividing")
        items: List[Tuple[PointTuple, str]] = []
        seq = self._seq_id
        for b in subdivide_bb(bb, self.split_factor):
            real_bb, city_list = get_bb_for(b, cities)
            if not city_list:
                continue
            if len(city_list) > 1:
                self._seq_id += 1
                sector_name = self.get_input_osm_name(self._seq_id)
                # seems like we need to go further with subdivision
                items.append((real_bb, sector_name))
                self.subdivide(real_bb, city_list, self._seq_id, level + 1)
            else:  # we have exactly one city
                log.debug("Exactly one city left in the subdivision, appending it")
                city = city_list[0]
                items.append((city["bb"], f"{city['key']}{SUFFIX}"))
        config = self.generate_config(input_osm_name, items)
        self.configs.append((parent_seq, config, seq))
