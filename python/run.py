from solstreets.azimuth_processor import AzimuthProcessor
from typing import Optional
import logging
import typer
import time
from datetime import datetime
from solstreets.loader import OSMLoader
from solstreets.dumper import StreetDumper
from solstreets.azimuth_processor import AzimuthProcessor, combine_segments

logging.basicConfig(level="DEBUG")
log = logging.getLogger(__file__)

DEFAULT_MIN_LENGTH = 100
DEFAULT_MAX_THRESHOLD = 1.0


def main(
    file_name: str = typer.Argument(..., help="Input geojson file to process"),
    output: str = typer.Argument(..., help="output file name, without extension"),
    rising_on_day: datetime = typer.Argument(..., help="specify the day of the sunrise", formats=["%Y-%m-%d"]),
    threshold: float = typer.Argument(
        DEFAULT_MAX_THRESHOLD, help="max allowed difference in degrees between sunrise and the street alignment"
    ),
    min_length: float = typer.Argument(DEFAULT_MIN_LENGTH, help="Minimum length of a segment to be considered"),
):
    t0 = time.time()
    loader = OSMLoader()
    processor = AzimuthProcessor(rising_on_day, threshold)
    street_segments = (
        ss for s in loader.read(file_name) for ss in processor.process_segments(s) if ss.sun_diff < threshold
    )
    dumper = StreetDumper()
    dumper.dump((ss for ss in street_segments if ss.length > min_length), output + ".geojson")
    dumper.dump_stats(processor.get_stats(), output + ".stats.json")
    t1 = time.time()
    log.info(f"Processed {output} in {t1-t0:,.3} seconds")


if __name__ == "__main__":
    typer.run(main)
