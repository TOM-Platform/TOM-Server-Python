import os
import pytest

from io import BytesIO
from PIL import Image
from shapely import Point, LineString
from shapely.ops import nearest_points

from APIs.google_maps import google_maps_api
from APIs.google_maps.google_maps_api import find_locations_google, find_directions_google, find_static_maps_google
from APIs.maps.direction_data import DirectionData
from APIs.maps.location_data import LocationData
from APIs.maps.maps import get_locations
from APIs.maps.maps_util import calculate_distance
from Utilities.file_utility import get_project_root
from Utilities.image_utility import get_similarity_images
from Tests.Unit.maps_tests.test_map_util import coordinates, size, threshold_distance
from base_keys import PLACES_OPTION_GOOGLE

locations_sample_response_google = [LocationData(address='Ang Mo Kio Ave 8, Singapore',
                                                 name='The Deck',
                                                 latitude=1.3682795,
                                                 longitude=103.8503844),
                                    LocationData(address='Computing Dr, Singapore',
                                                 name='The Deck',
                                                 latitude=1.2944323,
                                                 longitude=103.7725605),
                                    LocationData(address='2 Andover Rd, Singapore 509984',
                                                 name='The Deck Bar by Changi Beach Club',
                                                 latitude=1.3909075,
                                                 longitude=103.9748168),
                                    LocationData(address='209 Henderson Rd, Singapore 159551',
                                                 name='The Deck',
                                                 latitude=1.2815748,
                                                 longitude=103.8199716),
                                    LocationData(address='20 Warwick Rd, Singapore 139010',
                                                 name='The Deck',
                                                 latitude=1.288321,
                                                 longitude=103.7978444),
                                    LocationData(address='#01-26, 111 Jln Hang Jebat, Singapore 139532',
                                                 name='The Deck Media Group Pte. Ltd.',
                                                 latitude=1.2823257,
                                                 longitude=103.8455755),
                                    LocationData(address='2 Kallang Ave, #01-K1, Singapore 339407',
                                                 name='Deck Bar',
                                                 latitude=1.3124182,
                                                 longitude=103.8631868),
                                    LocationData(address='120A Prinsep St, Singapore 187937',
                                                 name='DECK',
                                                 latitude=1.3017242,
                                                 longitude=103.8516775),
                                    LocationData(address='409 Ang Mo Kio Ave 10, #409 AMK Market And Food Centre, '
                                                         'Singapore 560409',
                                                 name='Ice Blends The Deck',
                                                 latitude=1.362585,
                                                 longitude=103.8554236)]

directions_sample_response_google = DirectionData(start_time=0, update_time=1709824071849, dest_dist=1039,
                                                  dest_dist_str='1039 m', dest_duration=823, dest_duration_str='14 min',
                                                  curr_dist=35, curr_dist_str='35 m', curr_duration=36,
                                                  curr_duration_str='1 min',
                                                  curr_instr='Head west toward Kent Ridge Dr', curr_direction=189,
                                                  num_steps='9', waypoint_dist=251, waypoint_dist_str='0.3 km',
                                                  waypoint_duration=216, waypoint_duration_str='4 mins',
                                                  polyline=[[1.2932400000000002, 103.77310000000001],
                                                            [1.29323, 103.77288000000001],
                                                            [1.29325, 103.77279000000001],
                                                            [1.29333, 103.77260000000001],
                                                            [1.2934400000000001, 103.77223000000001],
                                                            [1.29333, 103.77225000000001],
                                                            [1.29325, 103.77223000000001],
                                                            [1.29322, 103.77223000000001],
                                                            [1.29315, 103.77224000000001],
                                                            [1.2930400000000002, 103.77269000000001],
                                                            [1.29295, 103.77283000000001], [1.29289, 103.77284],
                                                            [1.29279, 103.7728], [1.29278, 103.77274000000001],
                                                            [1.29305, 103.77176000000001], [1.29318, 103.77123],
                                                            [1.2933100000000002, 103.77105],
                                                            [1.2934700000000001, 103.77083],
                                                            [1.2936200000000002, 103.77067000000001],
                                                            [1.2939100000000001, 103.77044000000001],
                                                            [1.29407, 103.77033000000002],
                                                            [1.2945300000000002, 103.7702],
                                                            [1.2947000000000002, 103.77018000000001],
                                                            [1.29481, 103.77018000000001],
                                                            [1.2949400000000002, 103.77021],
                                                            [1.2950100000000002, 103.77028000000001],
                                                            [1.29508, 103.77039], [1.29516, 103.77051],
                                                            [1.2952000000000001, 103.77052],
                                                            [1.29546, 103.77063000000001],
                                                            [1.29567, 103.77076000000001],
                                                            [1.2958100000000001, 103.77081000000001],
                                                            [1.29587, 103.77082000000001],
                                                            [1.2960800000000001, 103.77079],
                                                            [1.29618, 103.77076000000001],
                                                            [1.2962300000000002, 103.77073000000001],
                                                            [1.2962600000000002, 103.77064000000001],
                                                            [1.2962300000000002, 103.77051],
                                                            [1.2961200000000002, 103.77011],
                                                            [1.296, 103.76988000000001],
                                                            [1.2959200000000002, 103.76981],
                                                            [1.29579, 103.76974000000001],
                                                            [1.2953000000000001, 103.76972],
                                                            [1.2951100000000002, 103.76969000000001]],
                                                  error_message='')

waypoints = [[1.2934043, 103.7730927], [1.2925769, 103.7725056], [1.2934142, 103.7704343], [1.2951112, 103.7697015]]
test_close_coordinate = Point(1.295184, 103.770554)
test_far_coordinate = Point(1.2969057, 103.7691498)


@pytest.mark.asyncio
async def test_locations_google_success(monkeypatch):
    async def mock_find_locations_google_impl(search_text, location):
        return locations_sample_response_google

    monkeypatch.setattr(google_maps_api, 'find_locations_google', mock_find_locations_google_impl)
    response = await get_locations("The Deck", PLACES_OPTION_GOOGLE, (1.3369344, 103.9027994))
    assert response == locations_sample_response_google


@pytest.mark.asyncio
async def test_directions_google_success(monkeypatch):
    async def mock_find_directions_google_impl(start_time, coordinates, bearing, ors_option):
        return directions_sample_response_google

    monkeypatch.setattr(google_maps_api, 'find_directions_google', mock_find_directions_google_impl)
    response = await find_directions_google(0, waypoints, 45)
    assert response.start_time == directions_sample_response_google.start_time
    assert response.dest_dist == directions_sample_response_google.dest_dist
    assert response.dest_dist_str == directions_sample_response_google.dest_dist_str
    assert response.dest_duration == directions_sample_response_google.dest_duration
    assert response.dest_duration_str == directions_sample_response_google.dest_duration_str
    assert response.curr_dist == directions_sample_response_google.curr_dist
    assert response.curr_dist_str == directions_sample_response_google.curr_dist_str
    assert response.curr_duration == directions_sample_response_google.curr_duration
    assert response.curr_duration_str == directions_sample_response_google.curr_duration_str
    assert response.curr_instr == directions_sample_response_google.curr_instr
    assert response.curr_direction == directions_sample_response_google.curr_direction
    assert response.num_steps == directions_sample_response_google.num_steps
    assert response.waypoint_dist == directions_sample_response_google.waypoint_dist
    assert response.waypoint_dist_str == directions_sample_response_google.waypoint_dist_str
    assert response.waypoint_duration == directions_sample_response_google.waypoint_duration
    assert response.waypoint_duration_str == directions_sample_response_google.waypoint_duration_str
    assert response.error_message == directions_sample_response_google.error_message

    nearest_close_point = nearest_points(LineString(response.polyline), test_close_coordinate)[0]
    close_dist = calculate_distance(test_close_coordinate.x, test_close_coordinate.y, nearest_close_point.x,
                                    nearest_close_point.y)
    assert close_dist < threshold_distance

    nearest_far_point = nearest_points(LineString(response.polyline), test_far_coordinate)[0]
    far_dist = calculate_distance(test_far_coordinate.x, test_far_coordinate.y, nearest_far_point.x,
                                  nearest_far_point.y)
    assert far_dist > threshold_distance


@pytest.mark.asyncio
async def test_static_maps_google_success():
    image_data = await find_static_maps_google(coordinates, size)
    actual_image = Image.open(BytesIO(image_data))
    assert actual_image.size == size
    assert actual_image.format == 'JPEG'

    file_path = os.path.join(get_project_root(), "Tests", "Unit", "maps_tests", "map_images", "google",
                             "static_map_1.jpeg")
    expected_image = Image.open(file_path)
    similarity = get_similarity_images(actual_image, expected_image, 5)
    assert similarity > 0.9
