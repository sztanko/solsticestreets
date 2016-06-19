f=`basename $1` 
tmp_dir="/tmp/osm/$f"

rm -rf $tmp_dir
mkdir -p $tmp_dir

outName=`echo $f | awk -F'.' '{print $1".wintersolstice.shp"}'` 
unzip $1 roads.* -d $tmp_dir
python  load.py $tmp_dir/roads.shp $tmp_dir/$outName
rm -rf ../json/$outName.geojson
ogr2ogr -f "GeoJSON" ../json/$outName.geojson $tmp_dir/$outName
#rm -rf $tmp_dir
