import asyncio

from APIs.maps.maps import get_static_maps, get_walking_directions
from APIs.maps.maps_config import MapsConfig
from APIs.maps.maps_util import calculate_distance
from DataFormat.ProtoFiles.Running import direction_data_pb2, random_routes_data_pb2, running_target_data_pb2, \
    running_place_data_pb2, running_live_data_pb2, running_summary_data_pb2, running_type_position_mapping_data_pb2, \
    route_data_pb2
from Services.running_service.running_current_data import RunningCurrentData
from Services.running_service.running_display import RunningDisplayPosition
from Services.running_service.running_exceptions import (
    InvalidProtoDataException,
    UnsupportedTrainingModeException,
    InvalidRouteIdException,
)
from Services.running_service.running_keys import (
    RUNNING_CAMERA_TABLE,
    RUNNING_DIRECTION_TABLE,
    RUNNING_EXERCISE_TABLE,
    WAYPOINTS_LIST_DATA,
    ERR_NO_WAYPOINTS,
)
from Services.running_service.running_service_config import RunningServiceConfig
from Services.running_service.running_service_params import (
    BaseParams,
    RunningUnitParams,
)
from Services.running_service.running_training_mode import RunningTrainingMode
from Utilities import time_utility
from Utilities.format_utility import convert_m_s_to_min_km


##############################################################################################################
############################################## Saving data ###################################################
##############################################################################################################


def save_real_waypoints(decoded_data):
    if not decoded_data or not decoded_data["waypoints_list"]:
        raise InvalidProtoDataException(WAYPOINTS_LIST_DATA, ERR_NO_WAYPOINTS)
    waypoints_list = []
    for waypoint in decoded_data["waypoints_list"]:
        waypoints_list.append([waypoint["lat"], waypoint["lng"]])
    RunningCurrentData.curr_lat = waypoints_list[0][0]
    RunningCurrentData.curr_lng = waypoints_list[0][1]
    if len(waypoints_list) > 1:
        RunningCurrentData.waypoints = waypoints_list


def save_real_running_data(running_coach_service, decoded_data):
    RunningCurrentData.start_time = int(decoded_data["start_time"])
    RunningCurrentData.curr_calories = int(decoded_data["calories"])
    RunningCurrentData.curr_heart_rate = int(decoded_data["heart_rate"])
    RunningCurrentData.curr_distance = decoded_data["distance"] / 1000
    RunningCurrentData.curr_speed = -1.0
    if decoded_data["speed"] != -1.0:
        RunningCurrentData.curr_speed = convert_m_s_to_min_km(decoded_data["speed"])
    RunningCurrentData.avg_speed = -1.0
    if RunningCurrentData.curr_distance != 0:
        RunningCurrentData.avg_speed = (
                                               BaseParams.total_sec / 60
                                       ) / RunningCurrentData.curr_distance
    RunningCurrentData.bearing = decoded_data["bearing"]
    if not (decoded_data["curr_lat"] == 0.0 and decoded_data["curr_lng"] == 0.0):
        RunningCurrentData.curr_lat = decoded_data["curr_lat"]
        RunningCurrentData.curr_lng = decoded_data["curr_lng"]
    json_data = {
        "start_time": RunningCurrentData.start_time,
        "calories": RunningCurrentData.curr_calories,
        "heart_rate": RunningCurrentData.curr_heart_rate,
        "distance": RunningCurrentData.curr_distance,
        "speed": RunningCurrentData.curr_speed,
        "avg_speed": RunningCurrentData.avg_speed,
        "bearing": RunningCurrentData.bearing,
        "curr_lat": RunningCurrentData.curr_lat,
        "curr_lng": RunningCurrentData.curr_lng,
        "timestamp": time_utility.get_current_millis(),
    }
    running_coach_service.insert_data_to_db(RUNNING_EXERCISE_TABLE, json_data)
    save_real_coords()


def save_real_coords(threshold_distance=RunningServiceConfig.threshold_coords_distance):
    if not (RunningCurrentData.curr_lat == 0.0 and RunningCurrentData.curr_lng == 0.0):
        if len(RunningCurrentData.coords) > 0:
            prev_lat, prev_lng = RunningCurrentData.coords[-1]

            distance = calculate_distance(
                prev_lat,
                prev_lng,
                RunningCurrentData.curr_lat,
                RunningCurrentData.curr_lng,
            )
            if distance >= threshold_distance:
                RunningCurrentData.coords.append(
                    [RunningCurrentData.curr_lat, RunningCurrentData.curr_lng]
                )
        else:
            RunningCurrentData.coords.append(
                [RunningCurrentData.curr_lat, RunningCurrentData.curr_lng]
            )


def save_training_mode_data(decoded_data):
    try:
        BaseParams.training_mode = RunningTrainingMode[decoded_data["detail"]]
    except KeyError as exc:
        raise UnsupportedTrainingModeException(decoded_data["detail"]) from exc


def save_direction_data(running_coach_service, direction_data):
    json_data = {
        "timestamp": time_utility.get_current_millis(),
        "start_time": RunningCurrentData.start_time,
        "dest_dist": direction_data.dest_dist,
        "dest_duration": direction_data.dest_duration,
        "curr_dist": direction_data.curr_dist,
        "curr_duration": direction_data.curr_duration,
        "curr_instr": direction_data.curr_instr,
        "curr_direction": direction_data.curr_direction,
    }
    running_coach_service.insert_data_to_db(RUNNING_DIRECTION_TABLE, json_data)


def save_running_camera_data(running_coach_service, decoded_data):
    json_data = {
        "timestamp": decoded_data["timestamp"],
        "position_x": decoded_data["position_x"],
        "position_y": decoded_data["position_y"],
        "position_z": decoded_data["position_z"],
        "rotation_x": decoded_data["rotation_x"],
        "rotation_y": decoded_data["rotation_y"],
        "rotation_z": decoded_data["rotation_z"],
    }
    running_coach_service.insert_data_to_db(RUNNING_CAMERA_TABLE, json_data)


##############################################################################################################
############################################## Building data #################################################
##############################################################################################################


def build_running_live_data(
        distance=None,
        heart_rate=None,
        speed=None,
        calories=None,
        duration=None,
        include_time=None,
):
    running_live_data_proto = running_live_data_pb2.RunningLiveData()

    if distance is not None:
        running_live_data_proto.distance = distance

    if heart_rate is not None:
        running_live_data_proto.heart_rate = f"{int(heart_rate)}"

    if speed is not None:
        if speed == -1.0:
            running_live_data_proto.speed = "N/A"
        else:
            running_live_data_proto.speed = f"{speed:.2f}"

    if calories is not None:
        running_live_data_proto.calories = f"{int(calories)}"

    if duration is not None:
        running_live_data_proto.duration = time_utility.get_hh_mm_ss_format(
            int(duration)
        )

    if include_time is True:
        running_live_data_proto.time = time_utility.get_date_string("%I:%M %p")

    return running_live_data_proto


def build_running_live_unit(distance="", heart_rate="", speed="", duration="", time=""):
    # TODO: add calories unit
    running_live_unit_proto = running_live_data_pb2.RunningLiveData(
        distance=distance,
        heart_rate=heart_rate,
        speed=speed,
        duration=duration,
        time=time,
    )

    return running_live_unit_proto


def build_running_alert(speed=None, distance=None, instruction=None, audio_instr=None):
    running_live_alert_proto = running_live_data_pb2.RunningLiveData(
        speed=speed,
        distance=distance,
        instruction=instruction,
        audio_instr=audio_instr
    )

    return running_live_alert_proto


def build_direction_data(
        dest_dist_str=None,
        dest_duration_str=None,
        curr_dist_str=None,
        curr_duration_str=None,
        curr_instr=None,
        curr_direction=None,
        audio_instr=None,
):
    direction_data_proto = direction_data_pb2.DirectionData()

    if dest_dist_str is not None:
        direction_data_proto.dest_dist = dest_dist_str

    if dest_duration_str is not None:
        direction_data_proto.dest_duration = dest_duration_str

    if curr_dist_str is not None:
        direction_data_proto.curr_dist = curr_dist_str

    if curr_duration_str is not None:
        direction_data_proto.curr_duration = curr_duration_str

    if curr_instr is not None:
        direction_data_proto.curr_instr = curr_instr

    if curr_direction is not None:
        direction_data_proto.curr_direction = str(curr_direction)

    if audio_instr is not None:
        direction_data_proto.audio_instr = audio_instr

    return direction_data_proto


def build_running_summary_data(
        exercise_type,
        start_place,
        start_time_string,
        distance,
        speed,
        duration,
        image,
        include_time=None,
):
    speed_value = "N/A"
    # default value of speed in protobuf is -1, if speed has not been recorded by server
    if speed != -1:  # FIXME: why -1?
        speed_value = f"{speed:.2f}"
    running_summary_data_proto = running_summary_data_pb2.RunningSummaryData(
        detail=f"{exercise_type} at {start_place} on {start_time_string}",
        distance=f"{distance:.2f}",
        speed=speed_value,
        duration=time_utility.get_hh_mm_format(int(duration)),
        image=image,
    )

    if include_time is True:
        running_summary_data_proto.time = time_utility.get_date_string("%I:%M %p")

    return running_summary_data_proto


def build_running_summary_unit(detail="", distance="", speed="", duration=""):
    running_summary_unit_proto = running_summary_data_pb2.RunningSummaryData(
        detail=detail,
        distance=distance,
        speed=speed,
        duration=duration,
    )

    return running_summary_unit_proto


def build_running_type_position_mapping():
    running_type_position_mapping_data_proto = (
        running_type_position_mapping_data_pb2.RunningTypePositionMappingData(
            running_distance_position=RunningDisplayPosition.BottomLeftTop.value,
            running_speed_position=RunningDisplayPosition.TopLeft.value,
            running_calories_position=RunningDisplayPosition.TopCenter.value,
            running_heart_rate_position=RunningDisplayPosition.TopRight.value,
            running_time_position=RunningDisplayPosition.BottomLeftBottom.value,
            summary_detail_position=RunningDisplayPosition.Top.value,
            summary_distance_position=RunningDisplayPosition.TopLeft.value,
            summary_speed_position=RunningDisplayPosition.TopCenter.value,
            summary_duration_position=RunningDisplayPosition.TopRight.value,
            summary_time_position=RunningDisplayPosition.BottomLeftBottom.value,
            selection_speed_position=RunningDisplayPosition.SelectionRight.value,
            selection_distance_position=RunningDisplayPosition.SelectionLeft.value,
        )
    )

    return running_type_position_mapping_data_proto


def build_random_routes_data(random_routes):
    random_route_data_proto = random_routes_data_pb2.RandomRoutesData()

    for route in random_routes:
        route_map_image = get_static_maps_image(
            route.direction_data.polyline, RunningServiceConfig.route_selection_map_size
        )
        route_data_proto = route_data_pb2.RouteData(
            route_id=route.route_id,
            route_map_image=route_map_image,
            dest_dist=f"{(route.direction_data.dest_dist / 1000):.2f}KM",
            dest_duration=route.direction_data.dest_duration_str,
            difficulty=route.difficulty,
            level=f"Lvl {(route.level)}",
            toilets=route.toilets,
            water_points=route.water_points,
        )
        random_route_data_proto.routes.append(route_data_proto)

    return random_route_data_proto


def build_running_target_data(distance=None, speed=None, training_mode=None):
    running_target_data_proto = running_target_data_pb2.RunningTargetData()

    if distance is not None:
        running_target_data_proto.distance = (
            f"{distance:.2f}{RunningUnitParams.distance.upper()}"
        )

    if speed is not None:
        running_target_data_proto.speed = (
            f"{speed:.2f}{RunningUnitParams.speed.upper()}"
        )

    if training_mode is not None:
        running_target_data_proto.training_mode = str(training_mode)

    return running_target_data_proto


def build_running_place_data(
        place_id=None,
        facility=None,
        location=None,
        level=None,
        distance=None,
        position=None,
):
    if distance is not None:
        distance = f"{distance}M"

    running_place_data_proto = running_place_data_pb2.RunningPlaceData(
        place_id=place_id,
        facility=facility,
        location=location,
        level=level,
        distance=distance,
        position=position,
    )
    return running_place_data_proto


##############################################################################################################
################################################# Utils ######################################################
##############################################################################################################

def get_chosen_route_id(decoded_data):
    try:
        route_id = int(decoded_data["detail"])
        if route_id < 1 or route_id > MapsConfig.sectors:
            raise InvalidRouteIdException(
                decoded_data["detail"],
                f"Route id {decoded_data['detail']} out of range.",
            )
        return int(decoded_data["detail"])
    except ValueError as exc:
        raise InvalidRouteIdException(
            decoded_data["detail"],
            f"Cannot parse route id {decoded_data['detail']} as int.",
        ) from exc


def get_directions(start_time, training_route, bearing, option, ors_option=0):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(
        get_walking_directions(start_time, training_route, bearing, option, ors_option)
    )
    loop.close()
    return result


def get_static_maps_image(coords, size):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    image_bytes = loop.run_until_complete(
        get_static_maps(coords, size, RunningServiceConfig.static_map_option)
    )
    loop.close()
    return image_bytes
