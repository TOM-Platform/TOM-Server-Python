from Services.running_service.running_current_data import RunningCurrentData
from Services.running_service.running_service_params import (
    BaseParams,
    DistanceTrainingParams,
)
from DataFormat import datatypes_helper
from Services.running_service.running_training_mode import RunningTrainingMode

# Table names
RUNNING_CAMERA_TABLE = "RunningCameraTable"
RUNNING_EXERCISE_TABLE = "RunningExerciseTable"
RUNNING_DIRECTION_TABLE = "RunningDirectionTable"

# DataTypes
EXERCISE_WEAR_OS_DATA = datatypes_helper.get_key_by_name("EXERCISE_WEAR_OS_DATA")
RUNNING_LIVE_DATA = datatypes_helper.get_key_by_name("RUNNING_LIVE_DATA")
RUNNING_LIVE_UNIT = datatypes_helper.get_key_by_name("RUNNING_LIVE_UNIT")
RUNNING_LIVE_ALERT = datatypes_helper.get_key_by_name("RUNNING_LIVE_ALERT")
RUNNING_SUMMARY_DATA = datatypes_helper.get_key_by_name("RUNNING_SUMMARY_DATA")
RUNNING_SUMMARY_UNIT = datatypes_helper.get_key_by_name("RUNNING_SUMMARY_UNIT")
DIRECTION_DATA = datatypes_helper.get_key_by_name("DIRECTION_DATA")
RUNNING_TYPE_POSITION_MAPPING_DATA = datatypes_helper.get_key_by_name(
    "RUNNING_TYPE_POSITION_MAPPING_DATA"
)
RANDOM_ROUTES_DATA = datatypes_helper.get_key_by_name("RANDOM_ROUTES_DATA")
ROUTE_DATA = datatypes_helper.get_key_by_name("ROUTE_DATA")
WAYPOINT_DATA = datatypes_helper.get_key_by_name("WAYPOINT_DATA")
WAYPOINTS_LIST_DATA = datatypes_helper.get_key_by_name("WAYPOINTS_LIST_DATA")
RUNNING_TARGET_DATA = datatypes_helper.get_key_by_name("RUNNING_TARGET_DATA")
RUNNING_CAMERA_DATA = datatypes_helper.get_key_by_name("RUNNING_CAMERA_DATA")

REQUEST_RUNNING_TRAINING_MODE_DATA = datatypes_helper.get_key_by_name(
    "REQUEST_RUNNING_TRAINING_MODE_DATA"
)
REQUEST_RUNNING_LIVE_DATA = datatypes_helper.get_key_by_name(
    "REQUEST_RUNNING_LIVE_DATA"
)
REQUEST_RUNNING_LIVE_UNIT = datatypes_helper.get_key_by_name(
    "REQUEST_RUNNING_LIVE_UNIT"
)
REQUEST_RUNNING_SUMMARY_DATA = datatypes_helper.get_key_by_name(
    "REQUEST_RUNNING_SUMMARY_DATA"
)
REQUEST_RUNNING_SUMMARY_UNIT = datatypes_helper.get_key_by_name(
    "REQUEST_RUNNING_SUMMARY_UNIT"
)
REQUEST_DIRECTION_DATA = datatypes_helper.get_key_by_name("REQUEST_DIRECTION_DATA")
REQUEST_RUNNING_TYPE_POSITION_MAPPING = datatypes_helper.get_key_by_name(
    "REQUEST_RUNNING_TYPE_POSITION_MAPPING"
)
REQUEST_RANDOM_ROUTES_DATA = datatypes_helper.get_key_by_name(
    "REQUEST_RANDOM_ROUTES_DATA"
)
REQUEST_CHOSEN_ROUTE_DATA = datatypes_helper.get_key_by_name(
    "REQUEST_CHOSEN_ROUTE_DATA"
)
REQUEST_RUNNING_TARGET_DATA = datatypes_helper.get_key_by_name(
    "REQUEST_RUNNING_TARGET_DATA"
)

# RunningDataHandler
ERR_NO_WAYPOINTS = "save_real_waypoints: No waypoints found"

# RunningService
INFO_WAIT_WEAROS_DATA = "Waiting for WearOS data..."

# RunningUiService
DEBUG_NONE_DATATYPE = "--- None datatype"
DEBUG_UNSUPPORTED_DATATYPE = "--- Unsupported datatype"

# TrainingModeSelectionService
INFO_TRAINING_MODE_SELECTED = f"Training mode: {BaseParams.training_mode}"

# RouteSelectionService
INFO_WAIT_CURRENT_LOCATION = "Waiting for current location..."
INFO_WAIT_FOR_ROUTE_REQUEST = "Waiting for route request..."
INFO_GENERATING_ROUTES = "Generating random routes..."
INFO_WAIT_FOR_CHOSEN_ROUTE = "Waiting for chosen route..."
ERR_GET_RANDOM_ROUTES = (
    "get_random_routes: generated_routes is None, route_selection is not running"
)
MESSAGE_LOCATION_NOT_AVAILABLE = "Current location not available!"
MESSAGE_SELECT_ROUTE = "Please select a route"

# RunningCoachService
INFO_RECEIVED_RUNNING_REQUEST = "Received running request"
INFO_RECEIVED_DIRECTION_REQUEST = "Received direction request"
INFO_PROCESSING_RUNNING_DATA = "Processing running data..."
INFO_PROCESSING_DIRECTION_DATA = "Processing direction data..."
INFO_WAYPOINT_REACHED = "Waypoint reached, removing waypoint from route"
MESSAGE_HALFWAY_NOTIF = "You're halfway there!\n"
MESSAGE_SPEED_UP = "Speed up!"
MESSAGE_SLOW_DOWN = "Slow down!"
MESSAGE_OFF_ROUTE = "You are off route!\n"
MESSAGE_DEST_REACHED = "Destination Reached!"
DIRECTION_STRAIGHT = "straight"


# generate_random_routes in maps.py
RUNNING_DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard"]


def info_chosen_route_id(route_id):
    return f"Chosen route id: {route_id}"


def info_destination_dist(distance):
    return f"Destination distance: {distance}"


def info_steps_message(curr_steps, total_steps):
    return f"curr_steps: {curr_steps}, total_steps: {total_steps}"


def info_curr_direction(direction):
    return f"Current direction: {direction}"


def info_curr_dist(distance):
    return f"Current distance: {distance}"


def warning_retry_direction_time(time_to_retry):
    return f"Directions data was requested too soon after recent error, retrying in {time_to_retry} seconds..."


def warning_deviating_count(deviation_update_count, deviation_update_threshold):
    return f"Deviation warning: {deviation_update_count}/{deviation_update_threshold}"


def err_chosen_route(route_id):
    return f"save_random_route: route_id {route_id} not found"


def err_get_socket_data_name(datatype_key):
    return datatypes_helper.get_name_by_key(datatype_key)


def message_get_dist_str():
    dist_str = f"{RunningCurrentData.curr_distance:.2f} KM"
    if BaseParams.training_mode == RunningTrainingMode.SpeedTraining:
        dist_str = f"{(DistanceTrainingParams.target_distance - RunningCurrentData.curr_distance):.2f} KM more"
    return dist_str
