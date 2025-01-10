import base_keys
from APIs.local_llm.local_translator import translate_text
from base_component import BaseComponent
from Utilities import logging_utility

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

        origin = raw_data[base_keys.ORIGIN_KEY]
        _logger.info("\nRaw_data: {origin}", origin=origin)

        if origin == base_keys.WHISPER_PROCESSOR:
            text = raw_data[base_keys.AUDIO_TRANSCRIPTION_DATA]

            translated = translate_text(text)
            _logger.info(
                "\nEnglish: {text}, Translated: {translated}",
                text=text,
                translated=translated,
            )
