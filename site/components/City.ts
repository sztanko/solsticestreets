export type City = {
    name: string;
    country: string;
    bb: [[number, number], [number, number]];
    key: string;
    area: number;
}

export type CityList = City[];