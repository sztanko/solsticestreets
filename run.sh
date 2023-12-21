#/bin/bash
set -e
set -x

source $1

data_dir="${data_dir:-/data}/$name"
repo_dir="${repo_dir:-/tmp/repo}"
source_file="$data_dir/source/input.osm.pbf"
source_file_highways="$data_dir/source/input-highways.osm.pbf"
geojson_destination="$data_dir/cities/"

# Function to send notification on failure
send_notification() {
    local error_message="$1"
    echo "$error_message" | ./send_notification.sh
}

# Trap errors and call send_notification function
trap 'send_notification "An error occurred in the script: $BASH_COMMAND"; exit 1' ERR

mkdir -p $(dirname $source_file)

wget -c -O $source_file $osm_url
echo "Removing all non-highway parts"
osmium tags-filter -O -o $source_file_highways $source_file w/highway
#rm $source_file
echo "Generating osmium configs for $cities_file"
python python/one_offs.py generate-osmium-configs $cities_file $data_dir $source_file_highways
echo "Extracting city pbf-s"
bash $data_dir/run.sh

mkdir -p $geojson_destination
rm -f $geojson_destination/*.*json
echo "Iterating through all city extracts"
export geojson_destination="$geojson_destination"

function get_streets() {
    local f=$1
    local filename=$(basename -- "$f")
    local key="${filename%%.*}"
    osmium export $f -f geojsonseq -O -r -o /dev/stdout | grep LineString | python python/run.py /dev/stdin $geojson_destination/$key 2020-12-21

}
export -f get_streets
ls $data_dir/pbf/*.osm.pbf | parallel get_streets
cp $data_dir/tree.geojson $geojson_destination # add subdivision plan

scripts/clone_and_commit.sh $geojson_destination $cities_file $repo_dir
echo "All done, cleaning up"
rm -rf $data_dir

echo "Hello, your new PR for solsticestreets data should be ready. Have a look at https://github.com/sztanko/solsticestreets/pulls" | ./send_notification.sh
