import asyncio
import threading

from APIs.maps.maps import generate_random_routes
from Services.running_service.running_current_data import RunningCurrentData
from Services.running_service.running_data_handler import (
    build_direction_data,
    build_random_routes_data,
    build_running_target_data,
    get_directions,
    get_chosen_route_id,
    save_real_waypoints,
)
from Services.running_service.running_service_config import RunningServiceConfig
from Services.running_service.running_service_params import (
    DistanceTrainingParams,
    BaseParams,
)
from Services.running_service.running_keys import (
    INFO_WAIT_CURRENT_LOCATION,
    MESSAGE_LOCATION_NOT_AVAILABLE,
    REQUEST_RANDOM_ROUTES_DATA,
    REQUEST_CHOSEN_ROUTE_DATA,
    WAYPOINTS_LIST_DATA,
    INFO_WAIT_FOR_ROUTE_REQUEST,
    INFO_GENERATING_ROUTES,
    INFO_WAIT_FOR_CHOSEN_ROUTE,
    ERR_GET_RANDOM_ROUTES,
    MESSAGE_SELECT_ROUTE,
    info_chosen_route_id,
    err_chosen_route,
)
from Utilities import time_utility, logging_utility
from base_component import BaseComponent
from base_keys import (
    COMPONENT_NOT_STARTED_STATUS,
    UNITY_CLIENT,
    COMPONENT_IS_STOPPED_STATUS,
    COMPONENT_IS_RUNNING_STATUS,
)

_logger = logging_utility.setup_logger(__name__)

class RouteSelectionService(BaseComponent):
    def __init__(self, name):
        super().__init__(name)
        super().set_component_status(COMPONENT_NOT_STARTED_STATUS)
        self.running_service = None
        self.random_routes = []

        # delay interval when current location from wearos client is not available yet
        self.wait_for_location_interval = 1  # sec
        # delay interval when route request from unity client is not received yet
        self.wait_for_route_request_interval = 1  # sec
        # delay interval when waiting for a user to select a route on unity client
        self.wait_for_chosen_route_interval = 1  # sec
        # delay interval for retry when no routes could be generated
        self.retry_generating_routes_interval = 5  # sec

    def run(self, running_service, socket_data_type, decoded_data, is_demo):
        # is_demo is to check if the service is running from demo config
        # purpose is to not save data from generated route and use demo route instead
        self.running_service = running_service
        self.get_route_data(socket_data_type, decoded_data, is_demo)

        if super().get_component_status() != COMPONENT_IS_RUNNING_STATUS:
            super().set_component_status(COMPONENT_IS_RUNNING_STATUS)

            # wait for current location to update
            # if no data is received from the watch, it defaults to (0.0, 0.0)
            # actual location cant be (0.0, 0.0) as that is in the middle of the ocean.
            while RunningCurrentData.curr_lat == 0 and RunningCurrentData.curr_lng == 0:
                _logger.info(INFO_WAIT_CURRENT_LOCATION)
                output_data = build_direction_data(
                    curr_instr=MESSAGE_LOCATION_NOT_AVAILABLE
                )
                self.running_service.send_to_component(
                    websocket_message=output_data, websocket_client_type=UNITY_CLIENT
                )
                time_utility.sleep_seconds(self.wait_for_location_interval)

            if not is_demo and RunningCurrentData.waypoints is not None:
                self.get_route_from_waypoints()
                return

            threading.Thread(
                target=self.get_random_route,
                args=(DistanceTrainingParams.target_distance, is_demo),
                daemon=True,
            ).start()

    @staticmethod
    def get_route_data(socket_data_type, decoded_data, is_demo):
        if socket_data_type is None:
            return
        if socket_data_type == REQUEST_RANDOM_ROUTES_DATA:
            BaseParams.request_queue.put(socket_data_type)
        elif socket_data_type == REQUEST_CHOSEN_ROUTE_DATA:
            BaseParams.chosen_route_id = get_chosen_route_id(decoded_data)
            BaseParams.request_queue.put(socket_data_type)
        elif socket_data_type == WAYPOINTS_LIST_DATA and not is_demo:
            save_real_waypoints(decoded_data)

    def get_route_from_waypoints(self):
        direction_data = get_directions(
            RunningCurrentData.start_time,
            RunningCurrentData.waypoints,
            RunningCurrentData.bearing,
            RunningServiceConfig.directions_option,
            RunningServiceConfig.ors_option,
        )
        RunningCurrentData.polyline = direction_data.polyline
        BaseParams.chosen_route_id = 1
        super().set_component_status(COMPONENT_IS_STOPPED_STATUS)

    def get_random_route(self, training_distance, is_demo):
        # wait for route request first
        while not BaseParams.is_item_in_queue(REQUEST_RANDOM_ROUTES_DATA):
            _logger.info(INFO_WAIT_FOR_ROUTE_REQUEST)
            time_utility.sleep_seconds(self.wait_for_route_request_interval)
        BaseParams.request_queue.queue.remove(REQUEST_RANDOM_ROUTES_DATA)
        _logger.info(INFO_GENERATING_ROUTES)
        self.send_random_routes(training_distance)

        # wait for choice by user
        while not BaseParams.is_item_in_queue(REQUEST_CHOSEN_ROUTE_DATA):
            _logger.info(INFO_WAIT_FOR_CHOSEN_ROUTE)
            time_utility.sleep_seconds(self.wait_for_chosen_route_interval)
        BaseParams.request_queue.queue.remove(REQUEST_CHOSEN_ROUTE_DATA)
        self.save_random_route(BaseParams.chosen_route_id, is_demo)

    def send_random_routes(self, training_distance):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.random_routes = loop.run_until_complete(
            self.get_random_routes(training_distance)
        )
        loop.close()

        output_data = build_random_routes_data(self.random_routes)
        self.running_service.send_to_component(
            websocket_message=output_data, websocket_client_type=UNITY_CLIENT
        )

        # to remove the generating route message
        output_data = build_direction_data(curr_instr=MESSAGE_SELECT_ROUTE)
        self.running_service.send_to_component(
            websocket_message=output_data, websocket_client_type=UNITY_CLIENT
        )

    async def get_random_routes(self, training_distance):
        generated_routes = None
        output_data = build_direction_data(curr_instr=INFO_GENERATING_ROUTES)
        self.running_service.send_to_component(
            websocket_message=output_data, websocket_client_type=UNITY_CLIENT
        )
        while super().get_component_status() == COMPONENT_IS_RUNNING_STATUS:
            origin = [RunningCurrentData.curr_lat, RunningCurrentData.curr_lng]
            generated_routes = await generate_random_routes(
                RunningCurrentData.start_time,
                RunningCurrentData.bearing,
                training_distance,
                origin,
                RunningServiceConfig.directions_option,
                RunningServiceConfig.ors_option,
            )
            if len(generated_routes) != 0:
                break
            time_utility.sleep_seconds(self.retry_generating_routes_interval)
        if generated_routes is not None:
            return generated_routes
        _logger.error(ERR_GET_RANDOM_ROUTES)

    def save_random_route(self, chosen_id, is_demo):
        # remove "please select a route" message
        output_data = build_direction_data()
        self.running_service.send_to_component(
            websocket_message=output_data, websocket_client_type=UNITY_CLIENT
        )

        chosen_route = None
        for route in self.random_routes:
            if route.route_id == chosen_id:
                _logger.info(info_chosen_route_id(route.route_id))
                chosen_route = route
        if chosen_route is None:
            _logger.error(err_chosen_route(chosen_id))
            return
        if not is_demo:
            RunningCurrentData.waypoints = chosen_route.waypoints
            RunningCurrentData.polyline = chosen_route.direction_data.polyline

        DistanceTrainingParams.target_distance = (
            chosen_route.direction_data.dest_dist / 1000
        )
        output_data = build_running_target_data(
            distance=DistanceTrainingParams.target_distance,
            training_mode=BaseParams.training_mode,
        )
        self.running_service.send_to_component(
            websocket_message=output_data, websocket_client_type=UNITY_CLIENT
        )

        super().set_component_status(COMPONENT_IS_STOPPED_STATUS)
