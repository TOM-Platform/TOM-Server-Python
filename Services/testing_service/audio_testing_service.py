import base_keys
from APIs.local_llm.local_translator import translate_text
from base_component import BaseComponent
from Services.template_service.template_data_handler import build_template_data
from Utilities import logging_utility

from ..template_service.template_service import TemplateService

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
            self._send_websocket_template_data(text=translated)

            _logger.info(
                "\nEnglish: {text}, Translated: {translated}",
                text=text,
                translated=translated,
            )

    def _send_websocket_template_data(
        self, text: str = "", image: bytes = None, audio_path: str = ""
    ) -> None:
        """
        Sending websocket data to the template scene

        :param text: text to be displayed
        :param image: bytes of the image
        :param audio_path: the audio file name without the extension.
            The audio file should be in the "Assets/Resources/Audio" folder of the Unity Client
        :return: None
        """
        websocket_template_data = build_template_data(
            text=text, image=image, audio_path=audio_path
        )

        super().send_to_component(websocket_message=websocket_template_data)

        _logger.info(
            "Sending Template Data (Text: {text}, Image, Audio: {audio_path}) sent to Template Scene",
            text=text,
            image=image,
            audio_path=audio_path,
        )
