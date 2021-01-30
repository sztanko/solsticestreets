#/bin/bash
set -e

source $1
data_dir="$base_data_dir/$name"
source_file="$data_dir/source/input.osm.pbf"
source_file_highways="$data_dir/source/input-highways.osm.pbf"

mkdir -p `dirname $source_file`

wget -c -O $source_file $osm_url
echo "Removing all non-highway parts"
osmium tags-filter -O -o $source_file_highways $source_file w/highway
echo "Generating osmium configs for $cities_file"
python python/one_offs.py generate-osmium-configs $cities_file $data_dir $source_file_highways
echo "Extracting city pbf-s"
bash $data_dir/run.sh
json_dir="$data_dir/geojson/"
mkdir -p $json_dir
echo "Iterating through all city extracts"
for f in $data_dir/pbf/*.osm.pbf
do
    echo $f
    filename=$(basename -- "$f")
    key="${filename%%.*}"
    osmium export $f -f geojsonseq -O -r -o /dev/stdout | python python/run.py /dev/stdin $json_dir/$key 2020-12-21
done