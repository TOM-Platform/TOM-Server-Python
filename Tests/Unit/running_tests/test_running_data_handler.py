import pytest

from Services.running_service import running_data_handler
from Tests.Integration.test_db_util import set_test_db_environ
from APIs.maps.direction_data import DirectionData
from APIs.maps.maps_config import MapsConfig
from APIs.maps.route_data import RouteData
from DataFormat.datatypes_helper import convert_json_to_protobuf

set_test_db_environ()
from Services.running_service.running_coach_service import RunningCoachService
from Services.running_service.running_current_data import RunningCurrentData
from Services.running_service.running_data_handler import (
    build_running_live_data,
    save_real_waypoints,
    save_real_coords,
    save_real_running_data,
    get_chosen_route_id,
    build_running_live_unit,
    build_running_alert,
    build_direction_data,
    build_running_summary_data,
    build_running_summary_unit,
    build_running_type_position_mapping,
    build_random_routes_data,
    build_running_target_data,
    get_directions,
    get_static_maps_image,
    save_training_mode_data,
)
from Services.running_service.running_display import RunningDisplayPosition
from Services.running_service.running_exceptions import (
    InvalidProtoDataException,
    UnsupportedTrainingModeException,
    InvalidRouteIdException,
)
from Services.running_service.running_keys import (
    ERR_NO_WAYPOINTS,
    WAYPOINTS_LIST_DATA,
    RUNNING_LIVE_DATA,
    RUNNING_LIVE_UNIT,
    RUNNING_LIVE_ALERT,
    DIRECTION_DATA,
    RUNNING_SUMMARY_UNIT,
    RUNNING_TYPE_POSITION_MAPPING_DATA,
    RANDOM_ROUTES_DATA,
    RUNNING_TARGET_DATA,
)
from Services.running_service.running_service_config import RunningServiceConfig
from Services.running_service.running_service_params import BaseParams
from Services.running_service.running_training_mode import RunningTrainingMode
from Tests.RunningFpv.running_demo_route import demo_waypoints
from Utilities.time_utility import (
    get_hh_mm_ss_format,
    get_date_string,
    get_hh_mm_format,
)

mock_running_coach_service = RunningCoachService(name="RunningCoachService")

test_start_time = 1635206400
test_calories = 200
test_heart_rate = 120
test_speed = 10  # min/km
test_distance = 5.0  # km
test_bearing = 90
test_duration = 60  # s

one_coord_waypoint_list = [
    {"waypoints_list": [{"lat": demo_waypoints[0][0], "lng": demo_waypoints[0][1]}]}
]
multi_coord_waypoint_list = [
    {
        "waypoints_list": [
            {"lat": demo_waypoints[0][0], "lng": demo_waypoints[0][1]},
            {"lat": demo_waypoints[1][0], "lng": demo_waypoints[1][1]},
        ]
    }
]
running_data = [
    {
        "start_time": test_start_time,
        "calories": test_calories,
        "heart_rate": test_heart_rate,
        "speed": 5 / 3,
        "speed_avg": 5 / 3,
        "distance": test_distance,
        "bearing": test_bearing,
        "curr_lat": demo_waypoints[0][0],
        "curr_lng": demo_waypoints[0][1],
    }
]
training_mode_data = [{"detail": "SpeedTraining"}]

test_direction_data_list = [
    DirectionData(
        start_time=0,
        update_time=1695779344571,
        dest_dist=1039,
        dest_dist_str="1039 m",
        dest_duration=823,
        dest_duration_str="14 min",
        curr_dist=35,
        curr_dist_str="35 m",
        curr_duration=36,
        curr_duration_str="1 min",
        curr_instr="Head west toward Kent Ridge Dr",
        curr_direction=189,
        num_steps="9",
        waypoint_dist=251,
        waypoint_dist_str="0.3 km",
        waypoint_duration=216,
        waypoint_duration_str="4 mins",
        error_message="",
    ),
    DirectionData(
        start_time=0,
        update_time=1688547782347,
        dest_dist=1572,
        dest_dist_str="1572 m",
        dest_duration=1132,
        dest_duration_str="19 min",
        curr_dist=36,
        curr_dist_str="36 m",
        curr_duration=26,
        curr_duration_str="1 min",
        curr_instr="Head east on Northbound, 7",
        curr_direction=42,
        num_steps="26",
        waypoint_dist=350,
        waypoint_dist_str="350 m",
        waypoint_duration=252,
        waypoint_duration_str="5 min",
        error_message="",
    ),
]

test_static_map_bytes = b"sxdafasd"


@pytest.fixture(autouse=True)
def clear_running_data():
    RunningCurrentData.reset()
    yield


@pytest.fixture(autouse=True)
def mock_insert_data_to_db(monkeypatch):
    monkeypatch.setattr(mock_running_coach_service, 'insert_data_to_db', lambda table_name, data: None)
    return mock_running_coach_service


@pytest.mark.parametrize("waypoint_data", [None, {}, {"waypoints_list": []}])
def test_save_real_waypoints_exceptions(waypoint_data):
    with pytest.raises(InvalidProtoDataException) as e:
        save_real_waypoints(waypoint_data)
    assert e.value.data_type == WAYPOINTS_LIST_DATA
    assert e.value.error_message == ERR_NO_WAYPOINTS


@pytest.mark.parametrize("waypoint_data", one_coord_waypoint_list)
def test_save_real_waypoints_one_coord(waypoint_data):
    save_real_waypoints(waypoint_data)
    assert RunningCurrentData.curr_lat == demo_waypoints[0][0]
    assert RunningCurrentData.curr_lng == demo_waypoints[0][1]
    assert RunningCurrentData.waypoints is None


@pytest.mark.parametrize("waypoint_data", multi_coord_waypoint_list)
def test_save_real_waypoints_multi_coords(waypoint_data):
    save_real_waypoints(waypoint_data)
    assert RunningCurrentData.curr_lat == demo_waypoints[0][0]
    assert RunningCurrentData.curr_lng == demo_waypoints[0][1]
    assert RunningCurrentData.waypoints == demo_waypoints[:2]


@pytest.mark.parametrize("decoded_data", running_data)
def test_save_real_running_data(monkeypatch, decoded_data):
    save_real_running_data(mock_running_coach_service, decoded_data)
    assert RunningCurrentData.start_time == test_start_time
    assert RunningCurrentData.curr_calories == test_calories
    assert RunningCurrentData.curr_heart_rate == test_heart_rate
    assert RunningCurrentData.curr_speed == test_speed
    assert RunningCurrentData.curr_distance == test_distance / 1000
    # TODO: mock BaseParams.total_sec
    # assert RunningCurrentData.avg_speed == test_speed
    assert RunningCurrentData.bearing == test_bearing
    assert RunningCurrentData.curr_lat == demo_waypoints[0][0]
    assert RunningCurrentData.curr_lng == demo_waypoints[0][1]


@pytest.mark.parametrize("decoded_data", running_data)
def test_save_real_running_data_invalid_speed(monkeypatch, decoded_data):
    save_real_running_data(mock_running_coach_service, decoded_data)
    decoded_data["speed"] = -1
    decoded_data["distance"] = 0
    save_real_running_data(mock_running_coach_service, decoded_data)
    assert RunningCurrentData.curr_speed == -1
    assert RunningCurrentData.avg_speed == -1


@pytest.mark.parametrize("decoded_data", running_data)
def test_save_real_running_data_no_location(monkeypatch, decoded_data):
    save_real_running_data(mock_running_coach_service, decoded_data)
    decoded_data["curr_lat"] = 0
    decoded_data["curr_lng"] = 0
    save_real_running_data(mock_running_coach_service, decoded_data)
    assert RunningCurrentData.curr_lat == demo_waypoints[0][0]
    assert RunningCurrentData.curr_lng == demo_waypoints[0][1]


def test_save_real_coords_zero():
    save_real_coords()
    assert RunningCurrentData.coords == []


def test_save_real_coords_first():
    RunningCurrentData.curr_lat = demo_waypoints[0][0]
    RunningCurrentData.curr_lng = demo_waypoints[0][1]
    save_real_coords()
    assert RunningCurrentData.coords == [demo_waypoints[0]]


def test_save_real_coords_multi_below_threshold():
    RunningCurrentData.curr_lat = demo_waypoints[0][0]
    RunningCurrentData.curr_lng = demo_waypoints[0][1]
    save_real_coords()
    RunningCurrentData.curr_lat = demo_waypoints[1][0]
    RunningCurrentData.curr_lng = demo_waypoints[1][1]
    save_real_coords()
    assert RunningCurrentData.coords == [demo_waypoints[0]]


def test_save_real_coords_multi_above_threshold():
    RunningCurrentData.curr_lat = demo_waypoints[0][0]
    RunningCurrentData.curr_lng = demo_waypoints[0][1]
    save_real_coords()
    RunningCurrentData.curr_lat = demo_waypoints[2][0]
    RunningCurrentData.curr_lng = demo_waypoints[2][1]
    save_real_coords()
    assert RunningCurrentData.coords == demo_waypoints[:3:2]


def test_save_real_coords_no_location():
    RunningCurrentData.curr_lat = demo_waypoints[0][0]
    RunningCurrentData.curr_lng = demo_waypoints[0][1]
    save_real_coords()
    RunningCurrentData.curr_lat = demo_waypoints[2][0]
    RunningCurrentData.curr_lng = demo_waypoints[2][1]
    save_real_coords()
    RunningCurrentData.curr_lat = 0
    RunningCurrentData.curr_lng = 0
    save_real_coords()
    assert RunningCurrentData.coords == demo_waypoints[:3:2]


@pytest.mark.parametrize("decoded_data", training_mode_data)
def test_save_training_mode_valid(decoded_data):
    save_training_mode_data(decoded_data)
    assert BaseParams.training_mode == RunningTrainingMode.SpeedTraining


@pytest.mark.parametrize("decoded_data", [{"detail": "SeedTraining"}])
def test_save_training_mode_invalid(decoded_data):
    with pytest.raises(UnsupportedTrainingModeException) as e:
        save_training_mode_data(decoded_data)
    assert e.value.training_mode == "SeedTraining"


@pytest.mark.parametrize("decoded_data", [{"detail": 1}])
def test_get_chosen_route_id_valid(decoded_data):
    assert get_chosen_route_id(decoded_data) == 1


@pytest.mark.parametrize("decoded_data", [{"detail": "wrong"}])
def test_get_chosen_route_id_value_error(decoded_data):
    with pytest.raises(InvalidRouteIdException) as e:
        get_chosen_route_id(decoded_data)
    assert e.value.error_message == "Cannot parse route id wrong as int."


@pytest.mark.parametrize("decoded_data", [{"detail": 0}])
def test_get_chosen_route_id_lower_bound(decoded_data):
    with pytest.raises(InvalidRouteIdException) as e:
        get_chosen_route_id(decoded_data)
    assert e.value.error_message == "Route id 0 out of range."


@pytest.mark.parametrize("decoded_data", [{"detail": MapsConfig.sectors + 1}])
def test_get_chosen_route_id_upper_bound(decoded_data):
    with pytest.raises(InvalidRouteIdException) as e:
        get_chosen_route_id(decoded_data)
    assert e.value.error_message == f"Route id {MapsConfig.sectors + 1} out of range."


def test_build_running_live_data():
    result_proto = build_running_live_data(
        distance=f"{test_distance:.2f}",
        heart_rate=test_heart_rate,
        speed=test_speed,
        calories=test_calories,
        duration=test_duration,
        include_time=True,
    )

    expected_running_live_data = {
        "distance": f"{test_distance:.2f}",
        "heart_rate": f"{int(test_heart_rate)}",
        "speed": f"{test_speed:.2f}",
        "calories": f"{test_calories}",
        "duration": get_hh_mm_ss_format(test_duration),
        "time": get_date_string("%I:%M %p"),
    }

    expected_running_live_data_proto = convert_json_to_protobuf(
        RUNNING_LIVE_DATA, expected_running_live_data
    )
    assert result_proto == expected_running_live_data_proto


def test_build_running_live_data_no_speed():
    result_proto = build_running_live_data(
        speed=-1,
    )

    expected_running_live_data = {
        "speed": "N/A",
    }

    expected_running_live_data_proto = convert_json_to_protobuf(
        RUNNING_LIVE_DATA, expected_running_live_data
    )

    assert result_proto == expected_running_live_data_proto


def test_build_running_live_unit():
    result_proto = build_running_live_unit(
        distance="km", heart_rate="bpm", speed="min/km", duration="AM", time="sec"
    )

    expected_running_live_unit = {
        "distance": "km",
        "heart_rate": "bpm",
        "speed": "min/km",
        "duration": "AM",
        "time": "sec",
    }

    expected_running_live_unit_proto = convert_json_to_protobuf(
        RUNNING_LIVE_UNIT, expected_running_live_unit
    )
    assert result_proto == expected_running_live_unit_proto


def test_build_running_alert():
    result_proto = build_running_alert(
        speed="true", distance="false", instruction="test", audio_instr=True
    )

    expected_running_alert = {
        "speed": "true",
        "distance": "false",
        "instruction": "test",
        "audio_instr": True,
    }

    expected_running_alert_proto = convert_json_to_protobuf(
        RUNNING_LIVE_ALERT, expected_running_alert
    )
    assert result_proto == expected_running_alert_proto


def test_build_direction_data():
    result_proto = build_direction_data(
        dest_dist_str=test_direction_data_list[0].dest_dist_str,
        dest_duration_str=test_direction_data_list[0].dest_duration_str,
        curr_dist_str=test_direction_data_list[0].curr_dist_str,
        curr_duration_str=test_direction_data_list[0].curr_duration_str,
        curr_instr=test_direction_data_list[0].curr_instr,
        curr_direction=test_direction_data_list[0].curr_direction,
        audio_instr=True,
    )

    expected_direction_data = {
        "dest_dist": test_direction_data_list[0].dest_dist_str,
        "dest_duration": test_direction_data_list[0].dest_duration_str,
        "curr_dist": test_direction_data_list[0].curr_dist_str,
        "curr_duration": test_direction_data_list[0].curr_duration_str,
        "curr_instr": test_direction_data_list[0].curr_instr,
        "curr_direction": str(test_direction_data_list[0].curr_direction),
        "audio_instr": True,
    }

    expected_direction_data_proto = convert_json_to_protobuf(
        DIRECTION_DATA, expected_direction_data
    )
    assert result_proto == expected_direction_data_proto


def test_build_running_summary_data():
    result_proto = build_running_summary_data(
        exercise_type="Running",
        start_place="NUS",
        start_time_string="10:00 AM",
        distance=test_distance,
        speed=test_speed,
        duration=test_duration,
        image=test_static_map_bytes,
        include_time=True,
    )

    assert result_proto.detail == "Running at NUS on 10:00 AM"
    assert result_proto.distance == f"{test_distance:.2f}"
    assert result_proto.speed == f"{test_speed:.2f}"
    assert result_proto.duration == f"{get_hh_mm_format(test_duration)}"
    assert result_proto.image == test_static_map_bytes
    assert result_proto.time == get_date_string("%I:%M %p")


def test_build_running_summary_data_no_speed():
    result_proto = build_running_summary_data(
        exercise_type="Running",
        start_place="NUS",
        start_time_string="10:00 AM",
        distance=test_distance,
        speed=-1,
        duration=test_duration,
        image=test_static_map_bytes,
        include_time=True,
    )

    assert result_proto.speed == "N/A"


def test_build_running_summary_unit():
    result_proto = build_running_summary_unit(
        detail="test", distance="km", speed="min/km", duration="sec"
    )

    expected_summary_unit = {
        "detail": "test",
        "distance": "km",
        "speed": "min/km",
        "duration": "sec",
    }

    expected_summary_unit_proto = convert_json_to_protobuf(
        RUNNING_SUMMARY_UNIT, expected_summary_unit
    )
    assert result_proto == expected_summary_unit_proto


def test_build_running_type_position_mapping():
    result_proto = build_running_type_position_mapping()

    expected_result = {
        "running_distance_position": RunningDisplayPosition.BottomLeftTop.value,
        "running_speed_position": RunningDisplayPosition.TopLeft.value,
        "running_calories_position": RunningDisplayPosition.TopCenter.value,
        "running_heart_rate_position": RunningDisplayPosition.TopRight.value,
        "running_time_position": RunningDisplayPosition.BottomLeftBottom.value,
        "summary_detail_position": RunningDisplayPosition.Top.value,
        "summary_distance_position": RunningDisplayPosition.TopLeft.value,
        "summary_speed_position": RunningDisplayPosition.TopCenter.value,
        "summary_duration_position": RunningDisplayPosition.TopRight.value,
        "summary_time_position": RunningDisplayPosition.BottomLeftBottom.value,
    }

    expected_result_proto = convert_json_to_protobuf(
        RUNNING_TYPE_POSITION_MAPPING_DATA, expected_result
    )
    assert result_proto == expected_result_proto


def test_build_random_routes_data():
    routes_data = [
        RouteData(
            route_id=1,
            waypoints=demo_waypoints[:2],
            direction_data=test_direction_data_list[0],
            difficulty="Easy",
            level=1,
            toilets=1,
            water_points=1,
        ),
        RouteData(
            route_id=2,
            waypoints=demo_waypoints[2:5],
            direction_data=test_direction_data_list[1],
            difficulty="Medium",
            level=2,
            toilets=2,
            water_points=2,
        ),
    ]

    result_proto = build_random_routes_data(routes_data)

    expected_routes_data = {
        "routes": [
            {
                "dest_dist": f"{round(test_direction_data_list[0].dest_dist / 1000, 2)}KM",
                "dest_duration": test_direction_data_list[0].dest_duration_str,
                "difficulty": "Easy",
                "level": "Lvl 1",
                "route_id": 1,
                "toilets": 1,
                "water_points": 1,
            },
            {
                "dest_dist": f"{round(test_direction_data_list[1].dest_dist / 1000, 2)}KM",
                "dest_duration": test_direction_data_list[1].dest_duration_str,
                "difficulty": "Medium",
                "level": "Lvl 2",
                "route_id": 2,
                "toilets": 2,
                "water_points": 2,
            },
        ]
    }

    expected_routes_data_proto = convert_json_to_protobuf(
        RANDOM_ROUTES_DATA, expected_routes_data
    )
    assert result_proto == expected_routes_data_proto


def test_build_running_target_data():
    result_dict = build_running_target_data(
        distance=test_distance,
        speed=test_speed,
    )

    expected_running_target_data = {
        "distance": f"{test_distance:.2f}KM",
        "speed": f"{test_speed:.2f}MIN/KM",
    }

    expected_running_target_data_proto = convert_json_to_protobuf(
        RUNNING_TARGET_DATA, expected_running_target_data
    )
    assert result_dict == expected_running_target_data_proto


def test_get_directions(monkeypatch):
    async def mock_get_walking_directions(
            start_time, waypoints, bearing, directions_option, ors_option
    ):
        return test_direction_data_list[0]

    monkeypatch.setattr(running_data_handler, 'get_walking_directions', mock_get_walking_directions)
    result = get_directions(
        test_start_time,
        demo_waypoints,
        test_bearing,
        RunningServiceConfig.directions_option,
        RunningServiceConfig.ors_option,
    )
    assert result == test_direction_data_list[0]


def test_get_static_maps_image(monkeypatch):
    async def mock_get_static_maps(coordinates, size, option):
        return test_static_map_bytes

    monkeypatch.setattr(running_data_handler, 'get_static_maps', mock_get_static_maps)
    result = get_static_maps_image(demo_waypoints, (400, 560))
    assert result == test_static_map_bytes
