import pytest
from shapely import Point, LineString
from shapely.ops import nearest_points

from APIs.maps.direction_data import DirectionData
from APIs.maps.maps import get_walking_directions
from APIs.maps.maps_util import calculate_distance
from APIs.ors_api import ors_api
from Tests.Unit.maps_tests.test_map_util import threshold_distance
from base_keys import DIRECTIONS_OPTION_ORS, ORS_OPTION_API, ORS_OPTION_DOCKER

directions_sample_response_ors = DirectionData(start_time=0, update_time=1709823008905, dest_dist=1576,
                                               dest_dist_str='1576 m', dest_duration=1135, dest_duration_str='19 min',
                                               curr_dist=36, curr_dist_str='36 m', curr_duration=26,
                                               curr_duration_str='1 min', curr_instr='Head east on Northbound, 7',
                                               curr_direction=42, num_steps='30', waypoint_dist=354,
                                               waypoint_dist_str='354 m', waypoint_duration=255,
                                               waypoint_duration_str='5 min',
                                               polyline=[[51.530578, -0.124315], [51.530596, -0.123798],
                                                         [51.530653, -0.123789], [51.530656, -0.123714],
                                                         [51.530629, -0.123709], [51.530629, -0.123736],
                                                         [51.530628, -0.123765], [51.53047, -0.123718],
                                                         [51.530458, -0.123802], [51.530339, -0.12403],
                                                         [51.530319, -0.124018], [51.53038, -0.123874],
                                                         [51.530372, -0.123825], [51.530419, -0.123717],
                                                         [51.530369, -0.123662], [51.530538, -0.123165],
                                                         [51.530762, -0.122602], [51.530733, -0.122565],
                                                         [51.530713, -0.122536], [51.530681, -0.122495],
                                                         [51.530672, -0.122489], [51.530688, -0.122342],
                                                         [51.530671, -0.122198], [51.530671, -0.122114],
                                                         [51.530718, -0.12213], [51.530739, -0.122085],
                                                         [51.530658, -0.121968], [51.530504, -0.121045],
                                                         [51.530551, -0.12102], [51.530588, -0.12103],
                                                         [51.530784, -0.121081], [51.530782, -0.121046],
                                                         [51.530784, -0.120973], [51.530786, -0.120904],
                                                         [51.530787, -0.120859], [51.530815, -0.120863],
                                                         [51.53088, -0.119828], [51.530815, -0.119466],
                                                         [51.530844, -0.119452], [51.530869, -0.119439],
                                                         [51.530894, -0.119427], [51.530909, -0.11941],
                                                         [51.530922, -0.119412], [51.530935, -0.119416],
                                                         [51.530943, -0.119329], [51.530994, -0.119296],
                                                         [51.531012, -0.119078], [51.531058, -0.118464],
                                                         [51.53108, -0.118201], [51.531173, -0.116981],
                                                         [51.531175, -0.116944], [51.531227, -0.116174],
                                                         [51.531234, -0.116083], [51.531257, -0.115997],
                                                         [51.531294, -0.11549], [51.531302, -0.115392],
                                                         [51.531339, -0.115081], [51.531318, -0.114984],
                                                         [51.53133, -0.114822], [51.531335, -0.114756],
                                                         [51.531304, -0.1147], [51.531328, -0.114344],
                                                         [51.531333, -0.114282], [51.531339, -0.114191],
                                                         [51.53137, -0.114121], [51.531381, -0.113932],
                                                         [51.531411, -0.11356], [51.531454, -0.112957],
                                                         [51.531458, -0.11292], [51.5315, -0.112411],
                                                         [51.531527, -0.112069], [51.531543, -0.111882],
                                                         [51.531551, -0.111797], [51.531576, -0.111558],
                                                         [51.531608, -0.111216], [51.531654, -0.110787],
                                                         [51.531684, -0.110536], [51.531691, -0.110479],
                                                         [51.531736, -0.110092], [51.531757, -0.109887],
                                                         [51.531777, -0.109696], [51.531809, -0.109153],
                                                         [51.531863, -0.107112], [51.531909, -0.106267],
                                                         [51.531913, -0.106221], [51.531946, -0.106145],
                                                         [51.531942, -0.106059], [51.531973, -0.106041],
                                                         [51.531982, -0.106035], [51.532048, -0.106152],
                                                         [51.532558, -0.106091], [51.532846, -0.105945],
                                                         [51.533046, -0.10581]],
                                               error_message='')

waypoints = [[51.5305457, -0.1243116], [51.5305794, -0.1211179], [51.531307, -0.1103626], [51.5330346, -0.1057646]]
test_close_coordinate = Point(51.5312668, -0.1131538)
test_far_coordinate = Point(51.5315631, -0.1053211)


@pytest.fixture
async def mock_find_directions_ors(monkeypatch):
    async def mock_find_directions_ors_impl(start_time, coordinates, bearing, ors_option):
        return directions_sample_response_ors

    monkeypatch.setattr(ors_api, 'find_directions_ors', mock_find_directions_ors_impl)
    yield mock_find_directions_ors_impl


@pytest.mark.asyncio
async def test_directions_ors_api_success(monkeypatch):
    response = await get_walking_directions(0, waypoints, 45, DIRECTIONS_OPTION_ORS, ORS_OPTION_API)
    assert_directions_response(response)


@pytest.mark.asyncio
async def test_directions_ors_localhost_success(monkeypatch):
    response = await get_walking_directions(0, waypoints, 45, DIRECTIONS_OPTION_ORS, ORS_OPTION_DOCKER)
    assert_directions_response(response)


def assert_directions_response(response):
    assert response.start_time == directions_sample_response_ors.start_time
    assert abs(response.dest_dist - directions_sample_response_ors.dest_dist) <= 5
    assert abs(response.dest_duration - directions_sample_response_ors.dest_duration) <= 5
    assert response.waypoint_duration == directions_sample_response_ors.waypoint_duration
    assert response.waypoint_duration_str == directions_sample_response_ors.waypoint_duration_str
    assert response.error_message == directions_sample_response_ors.error_message

    nearest_close_point = nearest_points(LineString(response.polyline), test_close_coordinate)[0]
    close_dist = calculate_distance(test_close_coordinate.x, test_close_coordinate.y, nearest_close_point.x,
                                    nearest_close_point.y)
    assert close_dist < threshold_distance

    nearest_far_point = nearest_points(LineString(response.polyline), test_far_coordinate)[0]
    far_dist = calculate_distance(test_far_coordinate.x, test_far_coordinate.y, nearest_far_point.x,
                                  nearest_far_point.y)
    assert far_dist > threshold_distance
