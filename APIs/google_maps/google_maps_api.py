# sources:
#   - https://developers.google.com/maps/documentation
#   - https://github.com/googlemaps/google-maps-services-python

import json
import math
import re
import time
from io import BytesIO
import googlemaps
import requests
from googlemaps.maps import StaticMapPath, StaticMapMarker
from PIL import Image
import base_keys
from APIs.maps.direction_data import DirectionData
from APIs.maps.location_data import LocationData
from APIs.maps.map_style import google_map_style
from APIs.maps.maps_util import calculate_bearing_after, calculate_turn_angle
from Utilities import file_utility, logging_utility
from Utilities.file_utility import get_credentials_file_path

GOOGLE_MAPS_CREDENTIAL_FILE = get_credentials_file_path(base_keys.GOOGLE_MAPS_CREDENTIAL_FILE_KEY_NAME)
KEY_MAP_API = 'map_api_key'
GOOGLE_MAP_BASE_STATIC_MAP_URL = "https://maps.googleapis.com/maps/api/staticmap"

_logger = logging_utility.setup_logger(__name__)


def read_google_maps_credential():
    '''

    :return: {"map_api_key": "YYY"}
    '''
    _logger.info('Reading Google Maps credentials')
    return file_utility.read_json_file(GOOGLE_MAPS_CREDENTIAL_FILE)


_credential = None
_client = None


def get_google_maps_credential(key, credential=None):
    global _credential

    if credential is None:
        _credential = read_google_maps_credential()
    else:
        _credential = credential

    return _credential[key]


def get_google_client():
    return googlemaps.Client(key=get_google_maps_credential(KEY_MAP_API))


# example of search_text can be like "The Deck, Singapore"
async def find_locations_google(search_text, location=None):
    global _client
    if _client is None:
        _client = get_google_client()

    params = {"query": search_text}
    if location is not None:
        params["location"] = location

    response = _client.places(**params)
    ''' example of successful response:
    {
      'html_attributions': [],
      'results': [
          {
            'business_status': 'OPERATIONAL',
            'formatted_address': 'Computing Dr, Singapore',
            'geometry': {
                'location': {
                  'lat': 1.2944323,
                  'lng': 103.7725605
                },
                'viewport': {
                    'northeast': {
                        'lat': 1.295730579892722,
                        'lng': 103.7739337298927
                    },
                    'southwest': {
                        'lat': 1.293030920107278,
                        'lng': 103.7712340701073
                    }
                }
            },
              'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/v1/png_71/restaurant-71.png',
              'icon_background_color': '#FF9E67',
              'icon_mask_base_uri': 'https://maps.gstatic.com/mapfiles/place_api/icons/v2/restaurant_pinlet',
              'name': 'The Deck',
              'opening_hours': {
                'open_now': True
              },
              'photos': [
                { ... }
              ],
              'place_id': 'ChIJVVVVJfka2jERZRl7AeJV__s',
              'plus_code': {
                'compound_code': '7QVF+Q2 Singapore',
                'global_code': '6PH57QVF+Q2'
              },
              'rating': 4.1,
              'reference': 'ChIJVVVVJfka2jERZRl7AeJV__s',
              'types': [
                'point_of_interest',
                'food',
                'establishment'
              ],
              'user_ratings_total': 741
            },
          },
          { ... } // second result
      ],
      'status': 'OK',    
    }
    '''

    location_data_list = []
    for result in response["results"]:
        lat_lng = result["geometry"]["location"]
        address = result.get("formatted_address", "")
        name = result["name"]
        lat = lat_lng["lat"]
        lng = lat_lng["lng"]

        location_data = LocationData(address, name, lat, lng)
        location_data_list.append(location_data)

    return location_data_list


async def find_directions_google(start_time, coordinates, bearing):
    global _client
    if _client is None:
        _client = get_google_client()

    src = coordinates[0]
    dest = coordinates[-1]
    waypoints = coordinates[1:-1]

    response = _client.directions(
        origin=src,
        destination=dest,
        waypoints=waypoints,
        mode="walking"
    )
    ''' example of successful response:
    {
        // google will try to locate the coordinates provided
        'geocoded_waypoints': [
            // 1st waypoint
            {
                "geocoder_status": "OK",
                "place_id": "ChIJVVVVJfka2jERZRl7AeJV__s",
                "types": [
                    "premise"
                ]
            },
            { ... } // 2nd waypoint
        ],
        "routes": [
            // 1st route suggested
            {
                "bounds": {
                    "northeast": {
                        "lat": 1.2957306,
                        "lng": 103.7739337
                    },
                    "southwest": {
                        "lat": 1.2930309,
                        "lng": 103.7712341
                    }                
                },
                "copyrights": "Map data ©2023 Google",
                "legs": [
                    // 1st waypoint to 2nd waypoint
                    {
                        "distance": {
                            "text": "0.1 km",
                            "value": 118 // in meters
                        },
                        "duration": {
                            "text": "2 mins",
                            "value": 97 // in seconds
                        },
                        "end_address": "21 Heng Mui Keng Terrace, Singapore 119613",
                        "end_location": {
                            "lat": 1.2924741,
                            "lng": 103.7759714
                        },
                        "start_address": "21 Heng Mui Keng Terrace, Singapore 119613",
                        "start_location": {
                            "lat": 1.2920947,
                            "lng": 103.7758751
                        },
                        // gps instructions to reach 2nd waypoint
                        "steps": [
                            {
                                "distance": {
                                    "text": "38 m",
                                    "value": 38 // in meters
                                },
                                "duration": {
                                    "text": "1 min",
                                    "value": 29 // in seconds
                                },
                                "end_location": {
                                    "lat": 1.292,
                                    "lng": 103.7761646
                                },
                                "html_instructions": /
                                "Head <b>east</b><div style=\"font-size:0.9em\">Restricted usage road</div>",
                                // encoded route line on map
                                "polyline": {
                                    "points": "qj{FgvkxRDSJc@"
                                },
                                "start_location": {
                                    "lat": 1.2920947,
                                    "lng": 103.7758751
                                },
                                "travel_mode": "WALKING"
                            },
                            { ... } // 2nd step
                        ]
                    }
                ]
            },
            { ... } // 2nd route suggested
        ],
        "status": "OK"
    }
    '''

    route = response[0]

    polyline = route['overview_polyline']['points']
    decoded_polyline = googlemaps.convert.decode_polyline(polyline)
    formatted_polyline = [[coord['lat'], coord['lng']]
                          for coord in decoded_polyline]

    num_steps = 0
    dest_dist = 0
    dest_duration = 0
    for leg in route['legs']:
        num_steps += len(leg['steps'])
        dest_dist += leg['distance']['value']
        dest_duration += leg['duration']['value']
    dest_dist_str = f"{dest_dist} m"
    dest_duration_str = f"{math.ceil(dest_duration / 60)} min"

    curr_leg = route['legs'][0]
    curr_dist = curr_leg['steps'][0]['distance']['value']
    curr_dist_str = curr_leg['steps'][0]['distance']['text']
    curr_duration = curr_leg['steps'][0]['duration']['value']
    curr_duration_str = curr_leg['steps'][0]['duration']['text']
    curr_instr = curr_leg['steps'][0]['html_instructions']
    curr_step_end_lat = curr_leg['steps'][0]['end_location']['lat']
    curr_step_end_lng = curr_leg['steps'][0]['end_location']['lng']
    curr_bearing_after = calculate_bearing_after(
        src[0], src[1], curr_step_end_lat, curr_step_end_lng)
    curr_direction = calculate_turn_angle(bearing, curr_bearing_after)
    waypoint_dist = curr_leg['distance']['value']
    waypoint_dist_str = curr_leg['distance']['text']
    waypoint_duration = curr_leg['duration']['value']
    waypoint_duration_str = curr_leg['duration']['text']

    return DirectionData(
        start_time=start_time,
        update_time=int(time.time() * 1000),
        dest_dist=dest_dist,
        dest_dist_str=dest_dist_str,
        dest_duration=dest_duration,
        dest_duration_str=dest_duration_str,
        curr_dist=curr_dist,
        curr_dist_str=curr_dist_str,
        curr_duration=curr_duration,
        curr_duration_str=curr_duration_str,
        # regex to remove html tags, from https://stackoverflow.com/a/12982689/18753727
        curr_instr=re.sub(re.compile(
            '<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});'), '', curr_instr),
        curr_direction=curr_direction,
        num_steps=str(num_steps),
        waypoint_dist=waypoint_dist,
        waypoint_dist_str=waypoint_dist_str,
        waypoint_duration=waypoint_duration,
        waypoint_duration_str=waypoint_duration_str,
        polyline=formatted_polyline
    )


async def find_static_maps_google_default(coordinates, size):
    global _client
    if _client is None:
        _client = get_google_client()

    path = StaticMapPath(points=coordinates, weight=3, color="red")

    markers = [StaticMapMarker(locations=coordinates[0], color="blue")]
    if len(coordinates) > 1:
        markers.append(StaticMapMarker(locations=coordinates[-1], color="red"))

    # successful response just returns the image of origin to destination encoded as bytes
    response = _client.static_map(size=size, path=path, format="jpg", markers=markers)
    static_map_bytes = b"".join(response)

    # Uncomment to save image in a jpg file
    image = Image.open(BytesIO(static_map_bytes))
    image.show()
    # image.save("static_map_1.jpeg", format="JPEG", quality=100)

    return static_map_bytes


async def find_static_maps_google(coordinates, size):
    # have to revert back to url because googlemaps python library doesn't support dark mode
    api_key = get_google_maps_credential(KEY_MAP_API)
    size_str = f"&size={size[0]}x{size[1]}"

    path = "&path=color:0xff0000ff|weight:3|" + "|".join([f"{lat},{lng}" for lat, lng in coordinates])
    # arrow_icon = "https://maps.google.com/mapfiles/dir_0.png"  # Replace with your custom arrow icon URL
    # # Add arrows every 15 coordinates
    # for i, (lat, lng) in enumerate(coordinates):
    #     if i % 15 == 0:
    #         path += f"|{lat},{lng}|icon:{arrow_icon}"
    #     else:
    #         path += f"|{lat},{lng}"

    style = google_map_style
    start_marker = f"&markers=color:blue|{coordinates[0][0]},{coordinates[0][1]}"
    end_marker = ""

    if len(coordinates) > 1:
        end_marker = f"&markers=color:red|{coordinates[-1][0]},{coordinates[-1][1]}"
    format_str = "&format=jpg"

    url = f"{GOOGLE_MAP_BASE_STATIC_MAP_URL}?key={api_key}{size_str}{path}{style}{start_marker}{end_marker}{format_str}"
    # successful response just returns the image of origin to destination encoded as bytes
    response = requests.get(url)

    if response.status_code == 200:
        static_map_bytes = response.content
        # Uncomment to show/save image in a jpg file
        image = Image.open(BytesIO(static_map_bytes))
        image.show()
        # image.save("static_map_1.jpeg", format="JPEG", quality=100)
        return static_map_bytes

    error_data = json.loads(response.content)
    error_message = error_data.get("message", "Unknown error")
    raise Exception(error_message)
