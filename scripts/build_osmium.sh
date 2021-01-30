mkdir work
cd work
OSMIUM_VERSION="2.15.1"
OSMIUM_TOOL_VERSION="1.13.0"

apt-get update && apt-get install -y wget g++ cmake cmake-curses-gui make libexpat1-dev zlib1g-dev libbz2-dev libsparsehash-dev libboost-program-options-dev libboost-dev libgdal-dev libproj-dev doxygen graphviz pandoc

mkdir /var/install
cd /var/install

wget https://github.com/osmcode/libosmium/archive/v${OSMIUM_VERSION}.tar.gz
tar xzvf v${OSMIUM_VERSION}.tar.gz
rm v${OSMIUM_VERSION}.tar.gz
mv libosmium-${OSMIUM_VERSION} libosmium

cd libosmium
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_EXAMPLES=OFF -DBUILD_TESTING=OFF -DINSTALL_PROTOZERO=ON ..
make

wget https://github.com/osmcode/osmium-tool/archive/v${OSMIUM_TOOL_VERSION}.tar.gz
tar xzvf v${OSMIUM_TOOL_VERSION}.tar.gz
rm v${OSMIUM_TOOL_VERSION}.tar.gz
mv osmium-tool-${OSMIUM_TOOL_VERSION} osmium-tool

cd osmium-tool
mkdir build && cd build
cmake -DOSMIUM_INCLUDE_DIR=/var/install/libosmium/include/ ..
make

mv /var/install/osmium-tool/build/src/osmium /usr/bin/osmium