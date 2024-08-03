import threading
from shapely import LineString, Point
from shapely.ops import nearest_points

from APIs.maps.maps_util import get_direction_str, calculate_distance
from Services.running_service import running_exceptions
from Services.running_service.running_current_data import RunningCurrentData
from Services.running_service.running_data_handler import (
    build_direction_data,
    build_running_live_data,
    build_running_alert,
    build_running_summary_data,
    get_directions,
    get_static_maps_image,
    save_direction_data,
    save_real_running_data,
    save_running_camera_data,
)
from Services.running_service.running_keys import (
    EXERCISE_WEAR_OS_DATA,
    RUNNING_CAMERA_DATA,
    RUNNING_SUMMARY_DATA,
    WAYPOINTS_LIST_DATA,
    REQUEST_RUNNING_LIVE_DATA,
    REQUEST_DIRECTION_DATA,
    REQUEST_RUNNING_SUMMARY_DATA,
    REQUEST_RANDOM_ROUTES_DATA,
    REQUEST_RUNNING_LIVE_UNIT,
    REQUEST_RUNNING_SUMMARY_UNIT,
    INFO_RECEIVED_RUNNING_REQUEST,
    INFO_RECEIVED_DIRECTION_REQUEST,
    warning_retry_direction_time,
    INFO_PROCESSING_RUNNING_DATA,
    MESSAGE_HALFWAY_NOTIF,
    MESSAGE_SPEED_UP,
    MESSAGE_SLOW_DOWN,
    INFO_PROCESSING_DIRECTION_DATA,
    INFO_WAYPOINT_REACHED,
    warning_deviating_count,
    MESSAGE_OFF_ROUTE,
    MESSAGE_DEST_REACHED,
    info_destination_dist,
    info_steps_message,
    DIRECTION_STRAIGHT,
    info_curr_direction,
    info_curr_dist,
    message_get_dist_str,
    RUNNING_LIVE_DATA,
    RUNNING_LIVE_ALERT,
)
from Services.running_service.running_service_config import RunningServiceConfig
from Services.running_service.running_service_params import (
    SpeedTrainingParams,
    BaseParams,
    DistanceTrainingParams,
)
from Services.running_service.running_training_mode import RunningTrainingMode
from Utilities import time_utility, logging_utility
from Utilities.format_utility import truncate_text
from base_component import BaseComponent
from base_keys import COMPONENT_NOT_STARTED_STATUS, UNITY_CLIENT, COMPONENT_IS_RUNNING_STATUS

_logger = logging_utility.setup_logger(__name__)

class RunningCoachService(BaseComponent):
    def __init__(self, name):

        super().__init__(name)
        super().set_component_status(COMPONENT_NOT_STARTED_STATUS)

        self.running_service = None
        self.running_coach_start_time = None
        self.ignored_data_types = [
            WAYPOINTS_LIST_DATA,
            REQUEST_RANDOM_ROUTES_DATA,
            REQUEST_RUNNING_LIVE_UNIT,
            REQUEST_RUNNING_SUMMARY_UNIT,
        ]

        # NOTE: To modify the frequency of running/direction requests, please modify the following variables in RunningController.cs
        # in TOM-Client-Unity project.
        #     private const int RUNNING_DATA_REQUEST_DELAY_SECONDS = 1;
        #     private const int DIRECTION_DATA_REQUEST_DELAY_SECONDS = 5;
        #     https://github.com/NUS-SSI/TOM-Client-Unity/blob/main/Assets/Scripts/Controller/RunningController.cs#L19-L20

        # time of latest known exercise start time
        self.latest_start_time = 0.0  # ms
        # distance interval (every "x" km) to display running UI
        self.dist_interval = 0.1  # km
        # curr_dist - prev_dist > dist_interval
        self.dist_interval_check = False

        # delay interval when waiting for a target data request from unity client
        self.wait_for_target_request_interval = 1  # sec
        # delay to check for either running or direction request
        self.training_update_interval = 0.2  # sec

        # the time of the previous running request when checking if curr_dist - prev_dist > dist_interval
        self.prev_running_request_time = -1  # ms
        # the delay when checking if curr_dist - prev_dist > dist_interval
        # e.g. assuming dist_interval = 0.4, running_ui_display_duration = 10
        # 0-10s: distance not reached, full running UI not displayed
        # 10-20s: distance interval reached (>0.4km for example), running data is displayed on Unity client
        # 20-30s: prev distance recorded, distance interval not reached with respect to prev distance, full running UI not displayed
        self.running_ui_display_duration = 10  # sec
        # similar to prev_running_request_time, but for direction request
        self.prev_direction_request_time = -1  # ms
        # similar to running_ui_display_duration, but for direction request
        # this is just a pure delay, since there is no need to check for dist_interval
        self.direction_ui_display_duration = 5  # sec

        # how many running instructions before playing audio
        self.audio_running_freq = 20
        # how many direction instructions before playing audio
        self.audio_direction_freq = 1
        # in ms, how long to wait before requesting directions again after recent error
        self.direction_error_interval = 10000
        # time of latest direction error
        self.latest_direction_error_time = -1

        self.is_correct_speed = False
        # +/- from target speed
        self.training_speed_tolerance = 0.5  # min/km

        # display directions only at this distance from turning point
        self.direction_distance_tolerance = 100  # m
        # min distance from waypoint to be considered reached
        self.waypoint_threshold = 20  # meters
        # min distance from destination to be considered reached
        self.dest_threshold = 10  # meters
        # max allowed perpendicular distance from route to be considered on route
        self.deviation_threshold = 30  # meters
        # number of direction updates before recalculating new route
        self.deviation_update_threshold = 3
        self.deviation_update_count = 0

    def run(self, running_service, socket_data_type, decoded_data):
        if not self.running_service:
            self.running_service = running_service
            self.running_coach_start_time = time_utility.get_current_millis()

        result = self.get_exercise_data(socket_data_type, decoded_data)
        if result is not None:
            self.running_service.send_to_component(
                websocket_message=result, websocket_client_type=UNITY_CLIENT
            )

        if super().get_component_status() != COMPONENT_IS_RUNNING_STATUS:
            threading.Thread(
                target=self.get_training_update,
                args=(
                    SpeedTrainingParams.target_speed,
                    DistanceTrainingParams.target_distance,
                ),
                daemon=True,
            ).start()
            super().set_component_status(COMPONENT_IS_RUNNING_STATUS)

    def get_exercise_data(self, socket_data_type, decoded_data):
        BaseParams.total_sec = (
            time_utility.get_current_millis() - self.running_coach_start_time
        ) / 1000
        if socket_data_type is None:
            return

        output_data = None

        if socket_data_type == EXERCISE_WEAR_OS_DATA:
            save_real_running_data(self, decoded_data)
            BaseParams.exercise_wear_os_count += 1

        elif socket_data_type == RUNNING_CAMERA_DATA:
            save_running_camera_data(self, decoded_data)

        elif socket_data_type == REQUEST_RUNNING_LIVE_DATA:
            # put request in queue to be processed later when speed or distance training is started
            _logger.info(INFO_RECEIVED_RUNNING_REQUEST)
            if not BaseParams.is_item_in_queue(REQUEST_RUNNING_LIVE_DATA):
                BaseParams.request_queue.put(socket_data_type)

        elif socket_data_type == REQUEST_DIRECTION_DATA:
            _logger.info(INFO_RECEIVED_DIRECTION_REQUEST)
            if not BaseParams.is_item_in_queue(REQUEST_DIRECTION_DATA):
                BaseParams.request_queue.put(socket_data_type)

        elif socket_data_type == REQUEST_RUNNING_SUMMARY_DATA:
            # get the last known coordinates if not already in the list
            if (
                RunningCurrentData.curr_lat,
                RunningCurrentData.curr_lng,
            ) not in RunningCurrentData.coords:
                RunningCurrentData.coords.append(
                    (RunningCurrentData.curr_lat, RunningCurrentData.curr_lng)
                )
            image = get_static_maps_image(
                RunningCurrentData.coords, RunningServiceConfig.summary_map_size
            )
            # TODO: get start_place from current location using places api
            output_data = build_running_summary_data(
                RunningCurrentData.exercise_type,
                RunningCurrentData.start_place,
                RunningCurrentData.start_time_string,
                RunningCurrentData.curr_distance,
                RunningCurrentData.avg_speed,
                BaseParams.total_sec,
                image,
                True,
            )
            self.running_service.send_to_component(
                websocket_message=output_data,
                websocket_datatype=RUNNING_SUMMARY_DATA,
                websocket_client_type=UNITY_CLIENT,
            )

        elif socket_data_type in self.ignored_data_types:
            return

        else:
            _logger.error(
                running_exceptions.UnsupportedDataTypeException(socket_data_type)
            )

    def get_training_update(self, training_speed, training_distance):
        while True:
            self.check_for_running_request(training_speed, training_distance)
            self.check_for_direction_request()
            time_utility.sleep_seconds(self.training_update_interval)

    def check_for_running_request(self, training_speed, training_distance):
        if BaseParams.is_item_in_queue(REQUEST_RUNNING_LIVE_DATA):
            BaseParams.running_count += 1
            if self.prev_running_request_time == -1:
                self.prev_running_request_time = time_utility.get_current_millis()
            time_diff = time_utility.get_current_millis() - self.prev_running_request_time
            if time_diff >= self.running_ui_display_duration * 1000:
                self.prev_running_request_time = time_utility.get_current_millis()
                self.dist_interval_check = (
                    RunningCurrentData.curr_distance - RunningCurrentData.prev_distance
                ) > self.dist_interval
                if self.dist_interval_check:
                    RunningCurrentData.prev_distance = RunningCurrentData.curr_distance

            self.process_running_request(training_distance, training_speed)
            with BaseParams.request_queue.mutex:
                BaseParams.request_queue.queue.remove(REQUEST_RUNNING_LIVE_DATA)

    def check_for_direction_request(self):
        if BaseParams.is_item_in_queue(REQUEST_DIRECTION_DATA):
            BaseParams.direction_count += 1
            if self.prev_direction_request_time == -1:
                self.prev_direction_request_time = time_utility.get_current_millis()
            time_diff = time_utility.get_current_millis() - self.prev_direction_request_time
            if time_diff >= self.direction_ui_display_duration * 1000:
                self.handle_direction_request_error()

    def handle_direction_request_error(self):
        # don't process direction request if there was an error recently
        self.prev_direction_request_time = time_utility.get_current_millis()
        error_time_diff = time_utility.get_current_millis() - self.latest_direction_error_time
        if self.latest_direction_error_time != -1 and error_time_diff < self.direction_error_interval:
            time_to_retry = round(
                (self.direction_error_interval - error_time_diff) / 1000, 1
            )
            _logger.warning(warning_retry_direction_time(time_to_retry))
        else:
            self.process_direction_request()
            with BaseParams.request_queue.mutex:
                BaseParams.request_queue.queue.remove(REQUEST_DIRECTION_DATA)

    def process_running_request(self, training_distance, training_speed):
        _logger.info(INFO_PROCESSING_RUNNING_DATA)
        half_distance_notif = False
        if BaseParams.training_mode == RunningTrainingMode.DistanceTraining:
            if RunningCurrentData.curr_distance >= training_distance / 2:
                if DistanceTrainingParams.half_dist_notif_timeout > 0:
                    half_distance_notif = True
                DistanceTrainingParams.half_dist_notif_timeout -= 1

                if not DistanceTrainingParams.halfway_point:
                    # change target speed to current average speed if distance training and at halfway point
                    DistanceTrainingParams.training_speed = RunningCurrentData.avg_speed
                    DistanceTrainingParams.halfway_point = True

                self.send_running_alert(
                    DistanceTrainingParams.training_speed, half_distance_notif
                )
        else:
            self.send_running_alert(training_speed, half_distance_notif)

        if self.dist_interval_check:
            output_data = build_running_live_data(
                message_get_dist_str(),
                RunningCurrentData.curr_heart_rate,
                RunningCurrentData.avg_speed,
                RunningCurrentData.curr_calories,
                BaseParams.total_sec,
                True,
            )
        elif (
            BaseParams.training_mode == RunningTrainingMode.DistanceTraining
            and not DistanceTrainingParams.halfway_point
        ):
            # dont show anything if halfway point not reached yet
            output_data = build_running_live_data(include_time=True)
        else:
            show_distance = half_distance_notif
            show_speed = not self.is_correct_speed
            if show_distance and show_speed:
                output_data = build_running_live_data(
                    speed=RunningCurrentData.avg_speed,
                    distance=message_get_dist_str(),
                    include_time=True,
                )
            elif show_distance:
                output_data = build_running_live_data(
                    distance=message_get_dist_str(), include_time=True
                )
            elif show_speed:
                output_data = build_running_live_data(
                    speed=RunningCurrentData.avg_speed, include_time=True
                )
            else:
                # TODO: maybe add an instruction to say user is on track?
                output_data = build_running_live_data(include_time=True)

        self.running_service.send_to_component(
            websocket_message=output_data,
            websocket_datatype=RUNNING_LIVE_DATA,
            websocket_client_type=UNITY_CLIENT,
        )

    def send_running_alert(self, training_speed, half_distance_notif):
        # choose whether to send audio instruction
        audio_instr = BaseParams.running_count % self.audio_running_freq == 0

        # convert boolean format to C#
        half_distance_notif_str = str(half_distance_notif).lower()
        instruction = ""
        if half_distance_notif:
            instruction = MESSAGE_HALFWAY_NOTIF

        self.is_correct_speed = (
            abs(RunningCurrentData.avg_speed - training_speed)
            <= self.training_speed_tolerance
        )
        if self.is_correct_speed and RunningCurrentData.avg_speed != -1.0:
            output_data = build_running_alert(
                distance=half_distance_notif_str,
                speed="false",
                instruction=instruction,
                audio_instr=audio_instr,
            )
        else:
            if (
                RunningCurrentData.avg_speed > training_speed
                or RunningCurrentData.avg_speed == -1.0
            ):
                instruction += MESSAGE_SPEED_UP
            else:
                instruction += MESSAGE_SLOW_DOWN

            output_data = build_running_alert(
                distance=half_distance_notif_str,
                speed="true",
                instruction=instruction,
                audio_instr=audio_instr,
            )

        self.running_service.send_to_component(
            websocket_message=output_data,
            websocket_datatype=RUNNING_LIVE_ALERT,
            websocket_client_type=UNITY_CLIENT,
        )

    def process_direction_request(self):
        _logger.info(INFO_PROCESSING_DIRECTION_DATA)
        # replace first coordinate with current coordinate
        RunningCurrentData.waypoints.pop(0)
        RunningCurrentData.waypoints.insert(
            0, [RunningCurrentData.curr_lat, RunningCurrentData.curr_lng]
        )

        direction_data = get_directions(
            RunningCurrentData.start_time,
            RunningCurrentData.waypoints,
            RunningCurrentData.bearing,
            RunningServiceConfig.directions_option,
            RunningServiceConfig.ors_option,
        )
        if direction_data.error_message != "":
            self.latest_direction_error_time = time_utility.get_current_millis()
            return
        self.parse_direction_result(direction_data)

    def parse_direction_result(self, direction_data):
        if direction_data is not None:
            save_direction_data(self, direction_data)
        # result can't be None, it just returns empty DirectionData if no data
        # so no need to check if result is None
        dest_dist_str = direction_data.dest_dist_str
        dest_dist = direction_data.dest_dist
        dest_duration_str = direction_data.dest_duration_str
        dest_duration = direction_data.dest_duration
        curr_dist_str = direction_data.curr_dist_str
        curr_dist = direction_data.curr_dist
        curr_duration_str = direction_data.curr_duration_str
        curr_duration = direction_data.curr_duration
        curr_instr = direction_data.curr_instr
        curr_direction = direction_data.curr_direction
        num_steps = direction_data.num_steps
        waypoint_dist = direction_data.waypoint_dist
        waypoint_dist_str = direction_data.waypoint_dist_str
        waypoint_duration = direction_data.waypoint_duration
        waypoint_duration_str = direction_data.waypoint_duration_str
        polyline = direction_data.polyline

        # truncate instruction if too long
        truncate_text(curr_instr, RunningServiceConfig.max_instruction_length)

        # Check if CurrentData is a new exercise/route (use start time to differentiate)
        if self.latest_start_time != RunningCurrentData.start_time:
            self.latest_start_time = RunningCurrentData.start_time
            # set total steps count to new route steps count
            RunningCurrentData.total_steps = int(num_steps)
            RunningCurrentData.polyline = polyline

        # if the user walks the wrong way, the total steps will be less than the current steps
        # so we need to update the total steps to the current steps
        if RunningCurrentData.curr_steps > RunningCurrentData.total_steps:
            RunningCurrentData.total_steps = int(num_steps)

        # Update number of current steps
        RunningCurrentData.curr_steps = int(num_steps)

        # if user is near waypoint, waypoint is considered to have been reached and remove waypoint from route
        if (
            waypoint_dist <= self.waypoint_threshold
            and len(RunningCurrentData.waypoints) > 2
        ):
            _logger.info(INFO_WAYPOINT_REACHED)
            RunningCurrentData.waypoints.pop(1)
        deviation_warning = self.check_deviation(polyline)

        if deviation_warning:
            curr_instr = MESSAGE_OFF_ROUTE + curr_instr
            
        self.send_directions(
            dest_dist,
            dest_dist_str,
            dest_duration_str,
            curr_dist,
            curr_dist_str,
            curr_duration_str,
            curr_instr,
            curr_direction,
            deviation_warning,
        )

    def check_deviation(self, polyline):
        deviation_warning = False
        curr_location = Point(RunningCurrentData.curr_lat, RunningCurrentData.curr_lng)
        polyline_line_string = LineString(RunningCurrentData.polyline)
        nearest_point = nearest_points(polyline_line_string, curr_location)[0]
        distance_from_route = calculate_distance(
            curr_location.x, curr_location.y, nearest_point.x, nearest_point.y
        )

        if distance_from_route > self.deviation_threshold:
            self.deviation_update_count += 1
            deviation_warning = True
            _logger.warning(
                warning_deviating_count(
                    self.deviation_update_count, self.deviation_update_threshold
                )
            )
            if self.deviation_update_count % self.deviation_update_threshold == 0:
                # recalculate route
                RunningCurrentData.polyline = polyline
        else:
            # reset count when user is back on track
            self.deviation_update_count = 0
        return deviation_warning

    def send_directions(
        self,
        dest_dist,
        dest_dist_str,
        dest_duration_str,
        curr_dist,
        curr_dist_str,
        curr_duration_str,
        curr_instr,
        curr_direction,
        deviation_warning,
    ):

        audio_instr = BaseParams.direction_count % self.audio_direction_freq == 0

        # we set a dest_radius for the user to be considered to have reached destination
        if RunningCurrentData.curr_steps == 1 and dest_dist <= self.dest_threshold:
            _logger.info(info_destination_dist(dest_dist_str))
            output_data = build_direction_data(
                curr_instr=MESSAGE_DEST_REACHED, audio_instr=True
            )

        elif deviation_warning:
            output_data = build_direction_data(
                dest_dist_str,
                dest_duration_str,
                curr_dist_str,
                curr_duration_str,
                curr_instr,
                curr_direction,
                audio_instr,
            )

        # check for first and last, always show direction data
        elif (
            RunningCurrentData.curr_steps == 1
            or RunningCurrentData.curr_steps == RunningCurrentData.total_steps
        ):
            _logger.info(
                info_steps_message(
                    RunningCurrentData.curr_steps, RunningCurrentData.total_steps
                )
            )
            output_data = build_direction_data(
                dest_dist_str,
                dest_duration_str,
                curr_dist_str,
                curr_duration_str,
                curr_instr,
                curr_direction,
                audio_instr,
            )

        # check for direction, don't show if straight
        elif get_direction_str(curr_direction) != DIRECTION_STRAIGHT:
            _logger.info(info_curr_direction(get_direction_str(curr_direction)))
            # check for distance, only show if close by like x meters for example
            if curr_dist <= self.direction_distance_tolerance:
                _logger.info(info_curr_dist(curr_dist_str))
                output_data = build_direction_data(
                    dest_dist_str,
                    dest_duration_str,
                    curr_dist_str,
                    curr_duration_str,
                    curr_instr,
                    curr_direction,
                    audio_instr,
                )
            else:
                # hide direction data
                output_data = build_direction_data()
        else:
            output_data = build_direction_data()

        self.running_service.send_to_component(
            websocket_message=output_data, websocket_client_type=UNITY_CLIENT
        )
