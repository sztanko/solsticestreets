p=`dirname $0`

wget -q https://raw.githubusercontent.com/migurski/Extractotron/master/cities.txt -O cities.txt
for i in `cat $p/cities.txt | tail -n +2 | awk -F'\t' '{print $7}'`
do
    echo "processing $i"
    time ./run-metro.sh $i $1
done

