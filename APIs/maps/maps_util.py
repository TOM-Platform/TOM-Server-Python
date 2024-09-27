# source: https://geographiclib.sourceforge.io/html/python/code.html
import math
import random
from geographiclib.geodesic import Geodesic
from Utilities import logging_utility

_logger = logging_utility.setup_logger(__name__)

KILOMETERS_TO_DEGREES = 1 / 111


def calculate_turn_angle(bearing_before, bearing_after):
    angle = bearing_after - bearing_before
    if angle < 0:
        angle += 360
    return angle


def get_direction_str(angle):
    if angle < 0 or angle >= 360:
        _logger.exception("Invalid angle provided: {angle}", angle=angle)
    if angle >= 350 or angle < 10:
        return "straight"
    direction_map = {
        (10, 45): "turn_slight_right",
        (45, 135): "turn_right",
        (135, 170): "turn_sharp_right",
        (170, 190): "u_turn",
        (190, 225): "turn_sharp_left",
        (225, 315): "turn_left",
        (315, 350): "turn_slight_left"
    }
    for direction_range, direction in direction_map.items():
        if direction_range[0] <= angle < direction_range[1]:
            return direction
    return "unknown"


# from https://stackoverflow.com/a/54875237/18753727
def calculate_bearing_after(src_lat, src_lng, dest_lat, dest_lng):
    return int(Geodesic.WGS84.Inverse(src_lat, src_lng, dest_lat, dest_lng)['azi1'])


def calculate_distance(lat1, lng1, lat2, lng2):
    return Geodesic.WGS84.Inverse(lat1, lng1, lat2, lng2)['s12']


def pick_random_points(center, radius, sectors, start_angle):
    points = [center]
    sector_angle = math.pi / sectors
    for i in range(sectors):
        angle = start_angle + sector_angle * i
        random_offset = random.uniform(0, sector_angle)
        angle += random_offset
        dx = radius * math.cos(angle) * KILOMETERS_TO_DEGREES
        dy = radius * math.sin(angle) * KILOMETERS_TO_DEGREES
        lat = center[0] + dy
        lng = center[1] + dx
        points.append([lat, lng])
    points.append(center)
    return points
