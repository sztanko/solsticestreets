import { MapContainer, Rectangle, TileLayer, GeoJSON } from "react-leaflet";
import { GeoJsonObject } from "geojson";
import type { City } from "./city";

import "leaflet/dist/leaflet.css";
import "leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.css";
import "leaflet-defaulticon-compatibility";

const CityMap = (props: {
  info: City;
  stats: Map<any, any>;
  streets: GeoJsonObject;
}) => {
  return (
    <MapContainer
      center={[30, 0]}
      zoom={2}
      scrollWheelZoom={true}
      style={{ height: "100%", width: "100%" }}
    >
      <TileLayer
        attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
        //url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        url="https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png"
      />
      <GeoJSON data={props.streets} />
    </MapContainer>
  );
};

export default CityMap;
