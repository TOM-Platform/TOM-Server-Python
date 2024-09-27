import threading
from base_keys import FPV_OPTION, WEBSOCKET_DATATYPE, WEBSOCKET_MESSAGE
from Services.running_service.running_keys import EXERCISE_WEAR_OS_DATA
from Services.running_service.running_current_data import RunningCurrentData
from Services.running_service.running_service_params import BaseParams
from Tests.RunningFpv.running_fpv_service import RunningFpvService
from Tests.RunningFpv.running_demo_route import demo_route, demo_waypoints, demo_distance, demo_bearing
from Utilities import environment_utility, logging_utility
from Utilities.format_utility import convert_m_s_to_min_km
from base_component import BaseComponent

_FPV_OPTION = environment_utility.get_env_int(FPV_OPTION)
_logger = logging_utility.setup_logger(__name__)


class RunningDemoService(BaseComponent):
    """
    RunningDemoService is responsible for simulating a demo running session.
    It handles the playback of demo routes, updates mock messages, and interacts with the FPV service.
    """

    def __init__(self, name):
        super().__init__(name)
        self.running_fpv_service = None
        self.prev_time_elapsed = 0
        self.mock_message = None
        self.add_mock_coords_for_summary = False

    def run(self, raw_data):
        if RunningCurrentData.waypoints is None:
            self.save_demo_waypoints()

        if self.running_fpv_service is None and BaseParams.running_count > 0:
            self.running_fpv_service = RunningFpvService()
            threading.Thread(target=self.running_fpv_service.run, daemon=True).start()

        websocket_data_type = raw_data[WEBSOCKET_DATATYPE]
        self.mock_message = raw_data[WEBSOCKET_MESSAGE]
        if websocket_data_type == EXERCISE_WEAR_OS_DATA:
            if self.running_fpv_service is None:
                self.set_null_island()
            else:
                self.demo_saving_data()

        super().send_to_component(websocket_message=self.mock_message, websocket_datatype=websocket_data_type)

    def save_demo_waypoints(self):
        RunningCurrentData.curr_lat = demo_route[0][0]
        RunningCurrentData.curr_lng = demo_route[0][1]
        RunningCurrentData.bearing = demo_bearing[0]
        RunningCurrentData.polyline = demo_route
        if _FPV_OPTION == 1:
            RunningCurrentData.waypoints = demo_waypoints[:3] + demo_waypoints[6:]
        else:
            RunningCurrentData.waypoints = demo_waypoints

    def set_null_island(self):
        self.mock_message['curr_lat'] = 0
        self.mock_message['curr_lng'] = 0

    def demo_saving_data(self):
        speed_in_min_km = convert_m_s_to_min_km(self.mock_message['speed'])
        self.running_fpv_service.set_treadmill_speed(speed_in_min_km)
        curr_time_elapsed = int(self.running_fpv_service.get_current_time() / 1000)
        # short fpv has 3 cuts, need to account here
        if _FPV_OPTION == 1:
            # 3rd cut, fpv_short jumps from 3:05 to 12:55 in normal fpv, therefore need to add 470 + 120 = 590 seconds
            if curr_time_elapsed >= 185:
                curr_time_elapsed += 590
            # 2nd cut, fpv_short jumps from 1:50 to 9:40 in normal fpv, therefore need to add 380 + 90 = 470 seconds
            elif curr_time_elapsed >= 110:
                # this is to add the skipped coords for summary map, \
                # so that the user doesn't just teleport for the route line
                if not self.add_mock_coords_for_summary:
                    for i in range(40, 116):
                        RunningCurrentData.coords.append(demo_route[i])
                    self.add_mock_coords_for_summary = True
                curr_time_elapsed += 470
            # 1st cut, fpv_short jumps from 1:20 to 2:50 in normal fpv, therefore need to add 90 seconds
            elif curr_time_elapsed >= 80:
                curr_time_elapsed += 90
        self.save_demo_running_data(curr_time_elapsed)
        _logger.info("curr_time_elapsed: {curr_time_elapsed}", curr_time_elapsed=curr_time_elapsed)
        if curr_time_elapsed - self.prev_time_elapsed >= 5:
            if int(curr_time_elapsed / 5) - 1 >= len(demo_route):
                _logger.warning("Demo finished")
                return
            if self.prev_time_elapsed != curr_time_elapsed:
                _logger.info("LatLng count: {count}", count=int(curr_time_elapsed / 5) - 1)
                self.save_demo_direction_params(int(curr_time_elapsed / 5) - 1)
            self.prev_time_elapsed = curr_time_elapsed

    def save_demo_running_data(self, curr_time_elapsed):
        try:
            if curr_time_elapsed > len(demo_distance) - 1:
                self.mock_message['distance'] = 1674
            self.mock_message['distance'] = demo_distance[curr_time_elapsed]
            self.mock_message['curr_lat'] = RunningCurrentData.curr_lat
            self.mock_message['curr_lng'] = RunningCurrentData.curr_lng
            self.mock_message['bearing'] = RunningCurrentData.bearing
            _logger.info(self.mock_message)
        except KeyError as e:
            _logger.error("Key not found: {exc}", exc=str(e))

    def save_demo_direction_params(self, latlng_count):
        try:
            self.mock_message['curr_lat'] = demo_route[latlng_count][0]
            self.mock_message['curr_lng'] = demo_route[latlng_count][1]
            self.mock_message['bearing'] = demo_bearing[latlng_count]
            _logger.info("lat: {lat}, lng: {lng}, bearing: {bearing}", lat=self.mock_message['curr_lat'],
                         lng=self.mock_message['curr_lng'], bearing=self.mock_message['bearing'], )

        except KeyError as e:
            _logger.error("Key not found: {exc}", exc=str(e))
