import React from "react";
import Link from "next/link";
import { MapContainer, Rectangle, TileLayer, Tooltip } from "react-leaflet";
import type { City } from "./City";

import "leaflet/dist/leaflet.css";
import "leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.css";
import "leaflet-defaulticon-compatibility";

function Rect(props: { city: City }) {
  const city = props.city;
  const bb = city.bb;
  return (
    <Rectangle
      bounds={[
        [bb[0][1], bb[0][0]],
        [bb[1][1], bb[1][0]],
      ]}
      eventHandlers={{
        click: () => {
          window.location.href = `/cities/${city.key}`;
        },
      }}
    >
      <Tooltip direction="bottom" offset={[0, 20]} opacity={1}>
        {city.name}, {city.country}
      </Tooltip>
    </Rectangle>
  );
}

const FrontMap = (c: { cities: City[] }) => {
  //console.log(c.cities);
  const cityRects = c.cities.map((city: City) => {
    return <Rect key={city.key} city={city} />;
  });
  return (
    <MapContainer
      center={[30, 0]}
      zoom={2}
      scrollWheelZoom={true}
      style={{ height: "800px", width: "100%" }}
    >
      <TileLayer
        attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
        //url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        url="https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png"
      />
      {cityRects}
    </MapContainer>
  );
};

export default FrontMap;
