import threading
from Utilities import logging_utility
from Services.running_service.running_keys import (
    EXERCISE_WEAR_OS_DATA,
    INFO_WAIT_WEAROS_DATA,
)
from Services.running_service.training_mode_selection_service import (
    TrainingModeSelectionService,
)
from base_keys import (
    COMPONENT_NOT_STARTED_STATUS,
    COMPONENT_IS_RUNNING_STATUS,
    ORIGIN_KEY,
    WEBSOCKET_MESSAGE,
    WEBSOCKET_DATATYPE,
    RUNNING_DEMO_SERVICE
)
from base_component import BaseComponent
from .route_selection_service import RouteSelectionService
from .running_coach_service import RunningCoachService
from .running_current_data import RunningCurrentData
from .running_service_params import BaseParams
from .running_ui_service import RunningUiService

_logger = logging_utility.setup_logger(__name__)


# For a visual representation of the flow of the running service,
# it can be found here: https://app.diagrams.net/#G1XB0Bq9sTHAix-52nNto3T1y3TD19FL4k
class RunningService(BaseComponent):
    """
    RunningService is responsible for handling the entire flow of running coach functionalities
    such as route selection, training mode management, coach services, and UI updates.

    Key functionalities:
    - Handles different states of running services like demo mode and wearOS data reception.
    - Manages the selection of routes and interaction with the running coach.
    - Runs UI updates and services in separate threads.
    - Maintains communication with other components using websocket messages.
    """

    def __init__(self, name):
        super().__init__(name)
        super().set_component_status(COMPONENT_NOT_STARTED_STATUS)
        self.route_selection_service = None
        self.running_coach_service = None
        self.running_ui_service = None
        self.training_mode_selection_service = None
        self.received_wear_os_data = False

    def run(self, raw_data):
        is_demo = raw_data[ORIGIN_KEY] == RUNNING_DEMO_SERVICE
        if super().get_component_status() != COMPONENT_IS_RUNNING_STATUS:
            BaseParams.reset()
            if not is_demo:
                RunningCurrentData.reset()
            super().set_component_status(COMPONENT_IS_RUNNING_STATUS)

        decoded_data = raw_data[WEBSOCKET_MESSAGE]
        socket_data_type = raw_data[WEBSOCKET_DATATYPE]

        if BaseParams.training_mode is None:
            if self.training_mode_selection_service is None:
                self.training_mode_selection_service = TrainingModeSelectionService(
                    "TrainingModeSelectionService"
                )
            threading.Thread(
                target=self.training_mode_selection_service.run,
                args=(self, socket_data_type, decoded_data),
                daemon=True,
            ).start()

        if self.running_ui_service is None:
            self.running_ui_service = RunningUiService("RunningUiService")
        threading.Thread(
            target=self.running_ui_service.run,
            args=(self, socket_data_type),
            daemon=True,
        ).start()

        if not self.received_wear_os_data:
            if socket_data_type != EXERCISE_WEAR_OS_DATA:
                _logger.info(INFO_WAIT_WEAROS_DATA)
                return
            self.received_wear_os_data = True

        if BaseParams.chosen_route_id == -1:
            if self.route_selection_service is None:
                self.route_selection_service = RouteSelectionService(
                    "RouteSelectionService"
                )
            threading.Thread(
                target=self.route_selection_service.run,
                args=(self, socket_data_type, decoded_data, is_demo),
                daemon=True,
            ).start()
        else:
            if self.running_coach_service is None:
                self.running_coach_service = RunningCoachService("RunningCoachService")
            threading.Thread(
                target=self.running_coach_service.run,
                args=(self, socket_data_type, decoded_data),
                daemon=True,
            ).start()
