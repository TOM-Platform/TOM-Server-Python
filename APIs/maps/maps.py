import math
import random
import socket

from googlemaps.exceptions import ApiError
from Utilities import logging_utility

from APIs.geoapify_api import geoapify_api
from APIs.maps import maps_util
from APIs.maps.direction_data import DirectionData
from APIs.maps.route_data import RouteData
from APIs.maps.maps_config import MapsConfig
from APIs.ors_api import ors_api
from APIs.osm_api import osm_api
from APIs.google_maps import google_maps_api
from Services.running_service.running_keys import RUNNING_DIFFICULTY_LEVELS
from base_keys import DIRECTIONS_OPTION_GOOGLE, DIRECTIONS_OPTION_ORS, PLACES_OPTION_GOOGLE, \
    PLACES_OPTION_OSM, STATIC_MAPS_OPTION_GEOAPIFY, STATIC_MAPS_OPTION_GOOGLE

_logger = logging_utility.setup_logger(__name__)


async def get_walking_directions(start_time, coordinates, bearing, option, ors_option=0):
    direction_data = DirectionData()
    try:
        if option == DIRECTIONS_OPTION_ORS:
            # Use OpenRouteService API
            direction_data = await ors_api.find_directions_ors(start_time, coordinates, bearing,
                                                               ors_option)
        elif option == DIRECTIONS_OPTION_GOOGLE:
            # Use Google Maps Directions API
            direction_data = await google_maps_api.find_directions_google(start_time, coordinates,
                                                                          bearing)
    except Exception as e:
        error_message = str(e)
        if isinstance(e, ApiError):
            error_message = "Google Maps API error occurred. Please try again later."
        # elif isinstance(e, MaxRouteLengthExceededException):
        #     error_message = "Route length exceeded. Please try again with a different location."
        elif isinstance(e, socket.timeout):
            error_message = "Connection timed out. Please check your internet connection."
        elif isinstance(e, socket.gaierror):
            error_message = "Failed to resolve hostname. Please check your internet connection."
        elif isinstance(e, socket.error):
            error_message = "Failed to connect to the server. Please check your internet connection."
        _logger.error("get_directions: {err_msg}", err_msg=error_message)
        direction_data.error_message = error_message

    return direction_data


async def generate_random_routes(start_time, bearing, target_dist, origin, option, ors_option=0):
    try:
        for i in range(0, 360, MapsConfig.angle_increment):
            # returns a set of points as part of a circle with radius {target_distance / dist_factor} and {
            # angle_increment} degrees
            waypoints = maps_util.pick_random_points(origin, target_dist / MapsConfig.dist_factor, MapsConfig.sectors,
                                                     i * math.pi / 180)
            direction_data = await get_walking_directions(start_time, waypoints, bearing, option,
                                                          ors_option)
            dest_dist = direction_data.dest_dist / 1000
            dist_diff = abs(dest_dist - target_dist)
            if dist_diff <= MapsConfig.dist_threshold * target_dist:
                route_data = RouteData(waypoints=waypoints, direction_data=direction_data,
                                       toilets=random.randint(0, 5),
                                       water_points=random.randint(0, 5))
                MapsConfig.possible_routes.append(route_data)
                if len(MapsConfig.possible_routes) == 3:
                    break
            else:
                if dest_dist < target_dist:
                    MapsConfig.dist_factor *= 1 - MapsConfig.dist_factor_growth  # increase circle radius
                else:
                    MapsConfig.dist_factor *= 1 + MapsConfig.dist_factor_growth  # decrease circle radius

        # Order possible_routes based on how close dest_dist is to target_distance
        ordered_routes = sorted(MapsConfig.possible_routes,
                                key=lambda x: abs(x.direction_data.dest_dist - target_dist))
        for i, route in enumerate(ordered_routes):
            route.difficulty = RUNNING_DIFFICULTY_LEVELS[i]
            route.level = i + 1
            route.route_id = i + 1

        return ordered_routes

    except Exception as e:
        error_message = str(e)
        _logger.error("generate_random_routes: {err_msg}", err_msg=error_message)
        return [], DirectionData(error_message=error_message)


async def get_locations(search_text, option, location=None):
    try:
        if option == PLACES_OPTION_OSM:
            # Use Nominatim OpenStreetMap API
            return await osm_api.find_locations_osm(search_text)
        if option == PLACES_OPTION_GOOGLE:
            # Use Google Maps Places API
            return await google_maps_api.find_locations_google(search_text, location)
    except Exception as e:
        error_message = str(e)
        if isinstance(e, ApiError):
            error_message = "Google Maps API error occurred. Please try again later."
        elif isinstance(e, socket.timeout):
            error_message = "Connection timed out. Please check your internet connection."
        elif isinstance(e, socket.gaierror):
            error_message = "Failed to resolve hostname. Please check your internet connection."
        elif isinstance(e, socket.error):
            error_message = "Failed to connect to the server. Please check your internet connection."
        _logger.error("get_locations: {err_msg}", err_msg=error_message)
        return []


async def get_static_maps(coordinates, size, option):
    try:
        if option == STATIC_MAPS_OPTION_GEOAPIFY:
            return await geoapify_api.find_static_maps_geoapify(coordinates, size)
        if option == STATIC_MAPS_OPTION_GOOGLE:
            return await google_maps_api.find_static_maps_google(coordinates, size)
    except Exception as e:
        error_message = str(e)
        if isinstance(e, ApiError):
            error_message = "Google Maps API error occurred. Please try again later."
        elif isinstance(e, socket.timeout):
            error_message = "Connection timed out. Please check your internet connection."
        elif isinstance(e, socket.gaierror):
            error_message = "Failed to resolve hostname. Please check your internet connection."
        elif isinstance(e, socket.error):
            error_message = "Failed to connect to the server. Please check your internet connection."
        _logger.error("get_static_maps: {err_msg}", err_msg=error_message)
