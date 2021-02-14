import { promises as fs } from "fs";
import path from "path";
import dynamic from "next/dynamic";
import Link from "next/link";

import type { City, CityList } from "../components/City";

export async function getStaticProps() {
  const citiesConfig = path.join(process.cwd(), "public/cities.json");
  const cities: CityList = JSON.parse(await fs.readFile(citiesConfig, "utf8"));

  // By returning { props: posts }, the Blog component
  // will receive `posts` as a prop at build time
  return {
    props: {
      cities: cities,
    },
  };
}

function CityIndex(props: { cities: CityList }) {
  const cities = props.cities;
  const cityEnum = cities.map((c) => (
    <li key={c.key}>
      <Link href={`/cities/${encodeURIComponent(c.key)}`} prefetch={false}>
        <a>
          {c.name}, {c.country}
        </a>
      </Link>
    </li>
  )); // <Link href={`/cities_${c.name}__${c.country}.html`}> </Link>
  return <ul className="city_list">{cityEnum}</ul>;
}

export default function Home(props: { cities: CityList }) {
  const cities = props.cities;
  const Map = dynamic(() => import("../components/FrontMap"), {
    ssr: false,
  });
  return (
    <div className="index">
      Hello
      <Map cities={cities} />
    </div>
  );
} //
