#/bin/bash
set -e

source $1
final_destination="site/cities/"
data_dir="$base_data_dir/$name"
source_file="$data_dir/source/input.osm.pbf"
source_file_highways="$data_dir/source/input-highways.osm.pbf"

mkdir -p `dirname $source_file`

wget -c -O $source_file $osm_url
echo "Removing all non-highway parts"
osmium tags-filter -O -o $source_file_highways $source_file w/highway
rm $source_file
echo "Generating osmium configs for $cities_file"
python python/one_offs.py generate-osmium-configs $cities_file $data_dir $source_file_highways
echo "Extracting city pbf-s"
bash $data_dir/run.sh

mkdir -p $final_destination
rm $final_destination/*.*json
echo "Iterating through all city extracts"
for f in $data_dir/pbf/*.osm.pbf
do
    echo $f
    filename=$(basename -- "$f")
    key="${filename%%.*}"
    osmium export $f -f geojsonseq -O -r -o /dev/stdout | grep LineString | python python/run.py /dev/stdin $final_destination/$key 2020-12-21
done
scripts/clone_and_commit.sh $final_destination /tmp/repo
echo "All done, cleaning up"
rm -rf $data_dir