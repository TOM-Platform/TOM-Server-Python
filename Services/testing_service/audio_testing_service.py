from Utilities import logging_utility
from base_component import BaseComponent
import base_keys

_logger = logging_utility.setup_logger(__name__)


class AudioTestingService(BaseComponent):
    """
    This service handles the processing and testing of raw audio data. It logs the raw data and manages the component's
    status.
    """

    def __init__(self, name) -> None:
        super().__init__(name)
        super().set_component_status(base_keys.COMPONENT_NOT_STARTED_STATUS)

    def run(self, raw_data):
        if super().get_component_status() != base_keys.COMPONENT_IS_RUNNING_STATUS:
            super().set_component_status(base_keys.COMPONENT_IS_RUNNING_STATUS)
        _logger.info("\nRaw_data: {data}", data=str(raw_data))
