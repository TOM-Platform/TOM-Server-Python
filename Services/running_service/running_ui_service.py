from Services.running_service.running_data_handler import (
    build_running_live_unit,
    build_running_summary_unit,
    build_running_target_data,
    build_running_type_position_mapping,
)
from Services.running_service.running_service_params import (
    DistanceTrainingParams,
    RunningUnitParams,
    SpeedTrainingParams,
    SummaryUnitParams,
)
from Services.running_service.running_keys import (
    DEBUG_NONE_DATATYPE,
    DEBUG_UNSUPPORTED_DATATYPE,
    EXERCISE_WEAR_OS_DATA,
    REQUEST_CHOSEN_ROUTE_DATA,
    REQUEST_RUNNING_LIVE_UNIT,
    REQUEST_RUNNING_SUMMARY_UNIT,
    REQUEST_RUNNING_TARGET_DATA,
    REQUEST_RUNNING_TRAINING_MODE_DATA,
    REQUEST_RUNNING_TYPE_POSITION_MAPPING,
    RUNNING_CAMERA_DATA,
    RUNNING_LIVE_UNIT,
    RUNNING_SUMMARY_UNIT,
    RUNNING_TARGET_DATA,
    RUNNING_TYPE_POSITION_MAPPING_DATA,
    REQUEST_DIRECTION_DATA,
    REQUEST_RUNNING_SUMMARY_DATA,
    REQUEST_RUNNING_LIVE_DATA,
    REQUEST_RANDOM_ROUTES_DATA,
    WAYPOINTS_LIST_DATA,
    err_get_socket_data_name,
)
from base_component import BaseComponent
from base_keys import COMPONENT_NOT_STARTED_STATUS, UNITY_CLIENT, COMPONENT_IS_RUNNING_STATUS
from Utilities import logging_utility

_logger = logging_utility.setup_logger(__name__)

class RunningUiService(BaseComponent):
    def __init__(self, name):
        super().__init__(name)
        super().set_component_status(COMPONENT_NOT_STARTED_STATUS)
        self.running_service = None
        self.unsupported_data_type = [
            REQUEST_RUNNING_SUMMARY_DATA,
            REQUEST_RUNNING_LIVE_DATA,
            REQUEST_RANDOM_ROUTES_DATA,
            REQUEST_DIRECTION_DATA,
            EXERCISE_WEAR_OS_DATA,
            WAYPOINTS_LIST_DATA,
            REQUEST_CHOSEN_ROUTE_DATA,
            REQUEST_RUNNING_TRAINING_MODE_DATA,
            RUNNING_CAMERA_DATA,
        ]

    def run(self, running_service, socket_data_type):
        if super().get_component_status() != COMPONENT_IS_RUNNING_STATUS:
            super().set_component_status(COMPONENT_IS_RUNNING_STATUS)
        self.running_service = running_service
        result, result_type = self.get_ui_config(socket_data_type)
        if result is not None:
            self.running_service.send_to_component(
                websocket_message=result,
                websocket_datatype=result_type,
                websocket_client_type=UNITY_CLIENT,
            )

    def get_ui_config(self, request_datatype):
        """
        :param request_datatype:
        :return: result, result_type
        """

        _logger.debug("get_ui_config: {type}", type = request_datatype)

        if request_datatype is None:
            _logger.debug(DEBUG_NONE_DATATYPE)
            return None, None

        if request_datatype in self.unsupported_data_type:
            _logger.debug(DEBUG_UNSUPPORTED_DATATYPE)
            return None, None

        if request_datatype == REQUEST_RUNNING_LIVE_UNIT:
            return (
                build_running_live_unit(
                    RunningUnitParams.distance,
                    RunningUnitParams.heart_rate,
                    RunningUnitParams.speed,
                    RunningUnitParams.duration,
                ),
                RUNNING_LIVE_UNIT,
            )

        elif request_datatype == REQUEST_RUNNING_SUMMARY_UNIT:
            return (
                build_running_summary_unit(
                    distance=SummaryUnitParams.distance,
                    speed=SummaryUnitParams.speed,
                    duration=SummaryUnitParams.duration,
                ),
                RUNNING_SUMMARY_UNIT,
            )

        elif request_datatype == REQUEST_RUNNING_TYPE_POSITION_MAPPING:
            return (
                build_running_type_position_mapping(),
                RUNNING_TYPE_POSITION_MAPPING_DATA,
            )

        elif request_datatype == REQUEST_RUNNING_TARGET_DATA:
            return (
                build_running_target_data(
                    distance=DistanceTrainingParams.target_distance,
                    speed=SpeedTrainingParams.target_speed,
                ),
                RUNNING_TARGET_DATA,
            )
        else:
            _logger.error(
                "--- Unknown datatype: {type}", type = err_get_socket_data_name(request_datatype)
            )
            return None, None
