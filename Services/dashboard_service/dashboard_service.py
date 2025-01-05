from Utilities import logging_utility
from base_keys import (
    COMPONENT_NOT_STARTED_STATUS,
    DASHBOARD_CLIENT,
    WEBSOCKET_MESSAGE,
    WEBSOCKET_DATATYPE,
    COMPONENT_IS_RUNNING_STATUS,
)
from base_component import BaseComponent
from DataFormat import datatypes_helper
from Services.running_service.running_keys import EXERCISE_WEAR_OS_DATA
from Services.dashboard_service.dashboard_data_handler import build_real_running_data_for_dashboard

DASHBOARD_LIVE_RUNNING_DATA = datatypes_helper.get_key_by_name("DASHBOARD_LIVE_RUNNING_DATA")

_logger = logging_utility.setup_logger(__name__)


class DashboardService(BaseComponent):
    """
    DashboardService is responsible for handling real-time websocket data and relaying it to the web client.
    """

    SUPPORTED_DATATYPES = {
        "DASHBOARD_LIVE_RUNNING_DATA", 
        "DASHBOARD_REQUEST_LIVE_DATA"
    }

    def __init__(self, name):
        super().__init__(name)
        super().set_component_status(COMPONENT_NOT_STARTED_STATUS)
        self.received_wear_os_data = False

    def run(self, raw_data):
        if super().get_component_status() != COMPONENT_IS_RUNNING_STATUS:
            super().set_component_status(COMPONENT_IS_RUNNING_STATUS)

        decoded_data = raw_data[WEBSOCKET_MESSAGE]
        socket_data_type = raw_data[WEBSOCKET_DATATYPE]

        if socket_data_type == EXERCISE_WEAR_OS_DATA:
            _logger.info("EXERCISE_WEAR_OS_DATA: ", decoded_data)
            data_for_dashboard = build_real_running_data_for_dashboard(decoded_data)
            self.send_to_component(
                websocket_message=data_for_dashboard,
                websocket_datatype=DASHBOARD_LIVE_RUNNING_DATA,
                websocket_client_type=DASHBOARD_CLIENT,
            )
