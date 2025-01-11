from Services.running_service.running_data_handler import (
    build_running_target_data,
    save_training_mode_data,
)
from Services.running_service.running_keys import INFO_TRAINING_MODE_SELECTED, REQUEST_RUNNING_TRAINING_MODE_DATA
from Services.running_service.running_service_params import (
    BaseParams,
    DistanceTrainingParams,
)
from base_component import BaseComponent
from base_keys import COMPONENT_NOT_STARTED_STATUS, UNITY_CLIENT, COMPONENT_IS_RUNNING_STATUS
from Utilities import logging_utility

_logger = logging_utility.setup_logger(__name__)


class TrainingModeSelectionService(BaseComponent):
    """
    Handles the selection of a training mode for running, such as distance or speed training.
    Processes the training mode selection data and sends the appropriate target data to the running service.
    """

    def __init__(self, name):
        super().__init__(name)
        super().set_component_status(COMPONENT_NOT_STARTED_STATUS)
        self.running_service = None

    def run(self, running_service, socket_data_type, decoded_data):
        if super().get_component_status() != COMPONENT_IS_RUNNING_STATUS:
            super().set_component_status(COMPONENT_IS_RUNNING_STATUS)

        self.running_service = running_service
        if socket_data_type == REQUEST_RUNNING_TRAINING_MODE_DATA:
            save_training_mode_data(decoded_data)
            _logger.info(INFO_TRAINING_MODE_SELECTED)
            BaseParams.request_queue.put(socket_data_type)
            # send distance of selected route as target distance
            output_data = build_running_target_data(
                distance=DistanceTrainingParams.target_distance,
                training_mode=BaseParams.training_mode,
            )
            self.running_service.send_to_component(websocket_message=output_data, websocket_client_type=UNITY_CLIENT)
