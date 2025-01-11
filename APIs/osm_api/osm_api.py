# source: https://nominatim.org/release-docs/latest/api/Overview/

import urllib.parse
import json
import aiohttp

from APIs.maps.location_data import LocationData

OSM_BASE_URL = "https://nominatim.openstreetmap.org/search"


# search_text = "Marina Bay Sands" for example
async def find_locations_osm(search_text):
    location_data_list = []

    query = urllib.parse.quote(search_text, safe='')
    url = f"{OSM_BASE_URL}?q={query}&format=geocodejson"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                response_data = await response.text()
                json_response = json.loads(response_data)
                ''' example of successful response:
                {
                    "type": "FeatureCollection",
                    "geocoding": { ... }, (just some metadata)
                    "features": [
                        // this is one feature, just repeat structure for multiple features
                        {
                            "type": "Feature",
                            "properties": {
                                "geocoding": {
                                "place_id": 251023553,
                                "osm_type": "node",
                                "osm_id": 4302905987,
                                "osm_key": "tourism",
                                "osm_value": "hotel",
                                "type": "house",
                                "label": "Marina Bay Sands, 10, Bayfront Avenue, Bayfront, Downtown Core, 
                                Singapore, Central, 018956, Singapore",
                                "name": "Marina Bay Sands"
                                }
                            },
                            "geometry": {
                                "type": "Point",
                                "coordinates": [
                                    103.8607226,
                                    1.2836965
                                ]
                            }
                        },
                        { ... }, // second search result
                        ...
                    ]
                }
                '''
                features = json_response["features"]
                for feature in features:
                    properties = feature["properties"]
                    geocoding = properties["geocoding"]
                    geometry = feature["geometry"]

                    address = geocoding.get("label", "")
                    name = geocoding.get("name", "")

                    lat = None
                    lng = None

                    if geometry["type"] == "Point":
                        coordinates = geometry["coordinates"]
                        lat = coordinates[1]
                        lng = coordinates[0]

                    location_data = LocationData(address, name, lat if lat is not None else 0.0,
                                                 lng if lng is not None else 0.0)
                    location_data_list.append(location_data)
            else:
                response_data = await response.text()
                json_response = json.loads(response_data)
                error = json_response["error"]
                message = error.get("message", "")
                raise Exception(f"OSM Error: {message}")

    return location_data_list
