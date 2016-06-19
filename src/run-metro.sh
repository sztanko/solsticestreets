# $1 - name of the city
# $2 - directory where to store out json files

export SHAPE_ENCODING="UTF-8"
SHAPE_ENCODING="UTF-8"
tmp_dir="/tmp/osm/$1"
#rm -rf $tmp_dir

mkdir -p $tmp_dir
mkdir -p $2
#cd $tmp_dir
wget -c https://s3.amazonaws.com/metro-extracts.mapzen.com/$1.imposm-shapefiles.zip -P $tmp_dir

rm $tmp_dir/$1.osm-roads.*
unzip $tmp_dir/$1.imposm-shapefiles *-roads.* -d $tmp_dir
rm -rf $tmp_dir/roads.shp
ogr2ogr -t_srs EPSG:4326 -s_srs EPSG:3857 $tmp_dir/roads.shp `ls $tmp_dir/*-roads.shp` -lco ENCODING=UTF-8
python  load.py $tmp_dir/roads.shp $tmp_dir/$1.shp $2/$1.stats.json
rm -rf $2/$1.geojson
ogr2ogr -f "GeoJSON" $2/$1.geojson $tmp_dir/$1.shp -lco ENCODING=UTF-8
rm -rf $tmp_dir/*.shp
rm -rf $tmp_dir/*.dbf
#rm -rf $tmp_dir
