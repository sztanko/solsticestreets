import { MapContainer, TileLayer, GeoJSON, useMap } from "react-leaflet";
import { GeoJsonObject } from "geojson";
import type { City } from "./City";
import Link from "next/link";
import * as d3 from "d3-scale";
import "leaflet/dist/leaflet.css";
import "leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.css";
import "leaflet-defaulticon-compatibility";
import { Control, LatLngExpression } from "leaflet";

function scaleOld(domain: number, range: number) {
  return (x: number) => {
    return (x * range) / domain;
  };
}

const StreetStatsControl = (props: {
  stats: any;
  city: City;
  width: number;
}) => {
  const numTicks = 16;
  const map = useMap();
  const r = (props.width * 0.9) / 2;
  const ticks = Array.from(Array(numTicks).keys()).map((i) => {
    const deg = (Math.PI / numTicks) * i;
    const x = r * Math.cos(deg);
    const y = r * Math.sin(deg);
    return <line x1={-x} y1={-y} x2={x} y2={y} key={deg} />;
  });
  const style = {
    width: props.width,
    height: props.width + 100,
  };

  const histogram = props.stats.street_histogram.map(Math.round);
  console.log(histogram);
  const maxLength = Math.max(...histogram);

  const histScale = d3.scaleLinear().domain([0, maxLength]).range([0, r]); // scale(maxLength, r);
  const step = Math.PI / 180;
  const xyFunc = (radius: number, azimuth: number) => {
    return [
      radius * Math.cos(azimuth - Math.PI / 2),
      radius * Math.sin(azimuth - Math.PI / 2),
    ];
  };

  const histogramPath = histogram.map((l: number, i: number) => {
    // console.log(i);
    // console.log(l);
    const R = histScale(l);
    const deg = i * step;

    const p0 = xyFunc(R, deg);
    const p1 = xyFunc(R, deg + step);
    // console.log([maxLength, R, deg, p0, p1]);
    const shape = `M0,0 L${p0[0]},${p0[1]} L${p1[0]},${
      p1[1]
    } L${-p1[0]},${-p1[1]} L${-p0[0]},${-p0[1]} L0,0`;
    // const shape = `M0,0 L${p0[0]},${p0[1]} L${p1[0]},${p1[1]} L0.0`;
    return <path d={shape} key={i} id={`path_${i}`} />;
  });
  console.log(props.stats);
  const azimuthLines = props.stats.sun_azimuths.map((az: number, i: number) => {
    const [x, y] = xyFunc(r, (az * Math.PI) / 180);
    return (
      <line
        x1={-x}
        y1={-y}
        x2={x}
        y2={y}
        className={`azimuth_line sun_azimuth_${i}`}
        key={i}
      />
    );
  });

  return (
    <div className="leaflet-bottom leaflet-left">
      <div className="leaflet-control leaflet-bar street-stats" style={style}>
        <h2>
          {props.city.name}, {props.city.country}
        </h2>
        <svg width={props.width} height={props.width}>
          <g transform={`translate(${props.width / 2}, ${props.width / 2})`}>
            <g className="base">
              <g className="ticks">{ticks}</g>
              <circle className="circle-p10" r={r * 1} cx={0} cy={0} />
              <circle className="circle-p9" r={r * 0.9} cx={0} cy={0} />
              <circle className="circle-p05" r={r * 0.5} cx={0} cy={0} />
            </g>

            <g className="streets">{histogramPath}</g>
            <g className="sun_azimuths">{azimuthLines}</g>
          </g>
        </svg>
        <p>
          <Link href="/">
            <a>&lt;&lt; Back to the city list</a>
          </Link>
        </p>
      </div>
    </div>
  );
};

const CityMap = (props: {
  info: City;
  stats: Map<any, any>;
  streets: GeoJsonObject;
}) => {
  const center: LatLngExpression = [
    (props.info.bb[0][1] + props.info.bb[1][1]) / 2,
    (props.info.bb[0][0] + props.info.bb[1][0]) / 2,
  ];
  const redScale = d3.scaleLinear().domain([0, 3]).range(["red", "white"]);
  const orangeScale = d3
    .scaleLinear()
    .domain([0, 3])
    .range(["orange", "white"]);
  const featureStyler = (feature) => {
    // console.log(feature);
    const colorScale = feature.properties.slope < 90 ? redScale : orangeScale;
    return { color: colorScale(feature.properties.sun_diff) }; //, dashArray: "3 1", fillColor: "orange" };
  };
  return (
    <MapContainer
      center={center}
      zoom={10}
      scrollWheelZoom={true}
      style={{ height: "100%", width: "100%" }}
    >
      <TileLayer
        attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
        //url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        url="https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png"
      />
      <GeoJSON data={props.streets} style={featureStyler} />
      <StreetStatsControl stats={props.stats} city={props.info} width={400} />
    </MapContainer>
  );
};

export default CityMap;
