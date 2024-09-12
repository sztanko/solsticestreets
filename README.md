[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/sztanko/solsticestreets)

solstreets
==========

Map of all streets pointing to the direction of the sun at first sunrise after winter solstice


## Adding new cities

To add new city, just add it in config/cities.json 
You only need to add name and country:
```
{
    "name": "Athens",
    "country": "United States",
}
```

Then run 
`python ./python/one_offs.py enrich-cities config/cities.json `

It will enrich the json with coordinates and everythign else.
Then commit.