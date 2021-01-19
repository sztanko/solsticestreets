# osmium export london_england.osm.pbf -o data.geojson
d="2020-12-22"
threshold="1"
min_length=10
osmium export $1.osm.pbf -f geojsonseq -r | grep LineString | grep highway | python python/run.py /dev/stdin $1 $d $threshold $min_length # best
