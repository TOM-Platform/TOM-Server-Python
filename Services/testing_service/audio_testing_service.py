import base_keys
from APIs.local_llm.local_translator import translate_text
from base_component import BaseComponent
from DataFormat import datatypes_helper
from Services.template_service.template_data_handler import build_template_data
from Utilities import logging_utility, time_utility

DATATYPE_REQUEST_TEMPLATE_DATA = datatypes_helper.get_key_by_name(
    "REQUEST_TEMPLATE_DATA"
)

_logger = logging_utility.setup_logger(__name__)


class AudioTestingService(BaseComponent):
    """
    This service handles the processing and testing of raw audio data. It logs the raw data and manages the component's
    status.
    """

    SUPPORTED_DATATYPES = {"TEMPLATE_DATA", "REQUEST_TEMPLATE_DATA"}

    def __init__(self, name) -> None:
        super().__init__(name)
        super().set_component_status(base_keys.COMPONENT_NOT_STARTED_STATUS)

        super().set_memory_data("last_updated", 0)

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

            self._save_translated_text(text, translated)

        if origin == base_keys.WEBSOCKET_WIDGET:
            datatype = raw_data[base_keys.WEBSOCKET_DATATYPE]
            data = raw_data[base_keys.WEBSOCKET_MESSAGE]

            data = datatypes_helper.convert_json_to_protobuf(datatype, data)
            _logger.debug("Template Service: {datatype}", datatype=datatype)

            self._handle_websocket_data(datatype, data)

    def _handle_websocket_data(self, socket_data_type, decoded_data):
        if socket_data_type == DATATYPE_REQUEST_TEMPLATE_DATA:
            self._handle_template_request(decoded_data)

    def _handle_template_request(self, request_data):
        _logger.info(
            "Template Request Data: {decoded_data}, {detail}",
            decoded_data=request_data,
            detail=request_data.detail,
        )
        current_millis = time_utility.get_current_millis()
        last_updated_millis = self._get_last_updated_time_millis()

        if current_millis - last_updated_millis > 3000:
            self._send_websocket_template_data(text="", image=None, audio_path="")

        try:
            ori_text, trans_text = self._get_text_translated()
            self._send_websocket_template_data(
                text=ori_text, image=None, audio_path=trans_text
            )
        except Exception:
            # No object is detected
            _logger.error("Error sending audio")

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

    # Set in the "shared" memory
    def _save_translated_text(self, ori_text, trans_text) -> None:
        super().set_memory_data("ori_text", ori_text)
        super().set_memory_data("trans_text", trans_text)
        super().set_memory_data("last_updated", time_utility.get_current_millis())

    # Get from "shared" memory
    def _get_text_translated(self) -> tuple:
        ori_text: str = super().get_memory_data("ori_text")
        trans_text: str = super().get_memory_data("trans_text")

        return ori_text, trans_text

    def _get_last_updated_time_millis(self) -> int:
        return super().get_memory_data("last_updated")
