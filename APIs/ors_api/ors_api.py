# source: https://openrouteservice.org/dev/#/api-docs
import math
import time

import openrouteservice

import base_keys
from APIs.maps import maps_util
from APIs.maps.direction_data import DirectionData
from Utilities import file_utility, logging_utility
from Utilities.file_utility import get_credentials_file_path

ORS_CREDENTIAL_FILE = get_credentials_file_path(base_keys.ORS_CREDENTIAL_FILE_KEY_NAME)
KEY_MAP_API = 'map_api_key'
_client = None

_logger = logging_utility.setup_logger(__name__)


def read_ors_credential():
    '''
    Read ORS credentials from file
    :return: {"map_api_key": "YYY"}
    '''
    _logger.info('Reading ORS credentials')
    return file_utility.read_json_file(ORS_CREDENTIAL_FILE)


def get_ors_credential(key, credential=None):
    _credential = credential

    if credential is None:
        _credential = read_ors_credential()
    else:
        _credential = credential

    return _credential[key]


def create_ors_client(option):
    if option == 0:
        return openrouteservice.Client(key=get_ors_credential(KEY_MAP_API))
    if option == 1:
        return openrouteservice.Client(base_url='http://localhost:8080/ors')
    raise ValueError("Invalid option.")


async def find_directions_ors(start_time, coordinates, bearing, option):
    global _client
    # lat lng is switched for ors
    switch_coordinates = [[coord[1], coord[0]] for coord in coordinates]

    if _client is None:
        _client = create_ors_client(option)
    response = _client.directions(switch_coordinates, profile='foot-walking', format="geojson", maneuvers=True)
    ''' example of successful response:
    {
        "type": "FeatureCollection",
        "metadata": { ... },
        // bounding box for whole route
        "bbox": [
            -0.124315,
            51.530319,
            -0.10581,
            51.533046
        ],
        "features": [
            // 1st route suggested
            {
                // not sure what is the difference with bbox on top
                'bbox': [
                    -0.124315,
                    51.530319,
                    -0.10581,
                    51.533046
                  ],
                "type": "Feature",
                'properties': {
                    'transfers': 0, // used for other forms of transport
                    'fare': 0, // used for other forms of transport
                    'segments': [
                        // 1st waypoint to 2nd waypoint
                        {
                            'distance': 349.7,
                            'duration': 252.1,
                            // gps instructions on how to reach 2nd waypoint
                            'steps': [
                                {
                                    'distance': 36.2, // distance from 1st waypoint, in meters
                                    'duration': 26.1, // duration from 1st waypoint, in seconds
                                    'type': 11, // not sure what this is, unused
                                    'instruction': 'Head east on Northbound, 7', // instruction to reach 2nd waypoint
                                    'name': 'Northbound, 7', // name of road
                                    'way_points': [ ... ] // not sure what this is, unused
                                    'maneuver': {
                                        // turning point location
                                        'location': [
                                            -0.124315,
                                            51.530578
                                        ],
                                        // direction user should be facing, but not used as we take actual user bearing
                                        // from watch/glasses instead
                                        'bearing_before': 0,
                                        // direction user should be facing after turning
                                        'bearing_after': 87
                                    }
                                },
                                {...}
                            ]            
                        },
                        { ... } // 2nd waypoint to 3rd waypoint
                    ],
                    'way_points': [ ... ], // not sure what this is, unused
                    'summary': {
                        'distance': 1572.1, // distance from origin to destination, in meters
                        'duration': 1132.1 // duration from origin to destination, in seconds
                    }
                },
                'geometry': {
                    'coordinates': [ ... ], // full route polyline suggested from origin to destination
                    'type': 'LineString'
                }
            },
            { ... } // 2nd route suggested
        ]
    }
    '''
    features = response["features"]
    properties = features[0]["properties"]
    polyline_coordinates = features[0]["geometry"]["coordinates"]
    # switch lat lng
    polyline = [[coord[1], coord[0]] for coord in polyline_coordinates]
    segments = properties["segments"]
    summary = properties["summary"]
    dest_dist = summary["distance"]
    dest_duration = summary["duration"]
    waypoint_dist = math.ceil(segments[0]["distance"])
    waypoint_dist_str = f"{waypoint_dist} m"
    waypoint_duration = math.ceil(segments[0]["duration"])
    waypoint_duration_str = f"{math.ceil(waypoint_duration / 60)} min"
    steps = segments[0]["steps"][:-1]

    curr_step = steps[0]
    curr_dist = curr_step["distance"]
    curr_duration = curr_step["duration"]
    curr_instr = curr_step["instruction"]
    curr_maneuver = curr_step["maneuver"]
    # curr_bearing_before = curr_maneuver["bearing_before"]
    curr_bearing_before = bearing
    curr_bearing_after = curr_maneuver["bearing_after"]
    curr_direction = maps_util.calculate_turn_angle(
        curr_bearing_before, curr_bearing_after)

    # last step in each segment is just 0m to indicate waypoint reached, so we use the second last step instead
    num_steps = 0
    for segment in segments:
        num_steps += len(segment["steps"])

    return DirectionData(
        start_time=start_time,
        update_time=int(time.time() * 1000),
        dest_dist=math.ceil(dest_dist),
        dest_dist_str=f"{math.ceil(dest_dist)} m",
        dest_duration=math.ceil(dest_duration),
        dest_duration_str=f"{math.ceil(dest_duration / 60)} min",
        curr_dist=math.ceil(curr_dist),
        curr_dist_str=f"{math.ceil(curr_dist)} m",
        curr_duration=math.ceil(curr_duration),
        curr_duration_str=f"{math.ceil(curr_duration / 60)} min",
        curr_instr=curr_instr,
        curr_direction=curr_direction,
        num_steps=str(num_steps),
        waypoint_dist=waypoint_dist,
        waypoint_dist_str=waypoint_dist_str,
        waypoint_duration=waypoint_duration,
        waypoint_duration_str=waypoint_duration_str,
        polyline=polyline
    )
