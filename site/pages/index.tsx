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
      ts: new Date().getTime(),
    },
  };
}

function groupBy(xs, f) {
  return xs.reduce(
    (r, v, i, a, k = f(v)) => ((r[k] || (r[k] = [])).push(v), r),
    {}
  );
}

function CityIndex(props: { cities: CityList }) {
  const cities_by_country = groupBy(props.cities, (x) => x.country);
  const countries = Object.entries(cities_by_country)
    .sort()
    .map(([country, cities], index) => {
      const cityEnum = cities.map((c) => (
        <li key={c.key}>
          <Link href={`/cities/${encodeURIComponent(c.key)}`} prefetch={false}>
            <a>{c.name}</a>
          </Link>
        </li>
      ));
      return (
        <div key={country} className="country">
          <h3>{country}</h3>
          <ul>{cityEnum}</ul>
        </div>
      );
    });
  return (
    <div className="city_list">
      <h2>City Index</h2>
      {countries}
    </div>
  );
}

export default function Home(props: { cities: CityList; ts: number }) {
  const cities = props.cities;
  const Map = dynamic(() => import("../components/FrontMap"), {
    ssr: false,
  });
  return (
    <div className="index">
      <h1>On Solstices and City Planning</h1>

      <article>
        <img src="stonehenge_plan.svg" className="header_image" />
        <p>
          Every year around 21st of December and 20th of June hundreds of people{" "}
          <a href="http://www.english-heritage.org.uk/daysout/properties/stonehenge/summer-solstice/?lang=en">
            gather to Stonehenge
          </a>{" "}
          to spot the fabulous attraction happening only twice a year - you can
          see how the central Altar stone aligns with the Slaughter stone, Heel
          stone and the rising sun to the northeast.
        </p>
        <p>
          Similar alignments can be found at{" "}
          <a href="http://en.wikipedia.org/wiki/Newgrange">
            Newgrange, Ireland
          </a>
          ,{" "}
          <a href="http://en.wikipedia.org/wiki/Maeshowe">Maeshowe, Scotland</a>{" "}
          and other prehistoric monuments. Winter solstice was very important in
          the life of ancient communities since it was seen as the beginning of
          the deep winter, and in the same time the reversal of the days
          shrinking was giving some hope for people. Same is true for the{" "}
          <a href="http://www.timeanddate.com/calendar/june-solstice-customs.html">
            Summer solstice
          </a>
        </p>

        <p>
          There are many streets in the cities which are aligned along the
          direction of rising sun of the solstice. I have found all of them.
          Unfortunately I don't know whether these alignments are intentional or
          just happen to be such on statistical basis. If you know the story of
          a such street, please send me a quick{" "}
          <a href="mailto:sztanko@gmail.com">email</a> and I will add this
          information.
        </p>
      </article>
      <h2>Choose your city to see the Stonehenge streets</h2>
      <div className="front-map">
        {" "}
        <Map cities={cities} />
      </div>
      <CityIndex cities={cities} />

      <h2>Thank you,</h2>
      <ul>
        <li>OpenStreetMap contributors for being so awesome</li>

        <li>
          Brandon Craig Rhodes for writing{" "}
          <a href="http://rhodesmill.org/pyephem/">ephem</a> a python library
          which I used to calculate the sun directions
        </li>
        <li>
          <a href="https://www.mapbox.com/">Mapbox</a> and{" "}
          <a href="https://github.com/mourner">Vladimir Agafonkin</a> for
          Leaflet and everything else map related
        </li>
        <li>Sabine Leitner for general inspiration</li>
      </ul>
      <footer>
        This project is open and free, soure available here:{" "}
        <a href="https://github.com/sztanko/solsticestreets">
          https://github.com/sztanko/solsticestreets
        </a>
        . <br /> Page last updated on {new Date(props.ts).toLocaleDateString()},{" "}
        {Math.floor((new Date().getTime() - props.ts) / 1000 / 3600 / 24)} days
        ago
      </footer>
    </div>
  );
} //
