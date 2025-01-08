import sys

from pymilvus import MilvusException

import base_keys
from DataFormat import datatypes_helper
from Utilities import logging_utility, time_utility, image_utility
from base_component import BaseComponent
from . import memory_keys
from .memory_assistance_config import MemoryAssistanceConfig
from .memory_assistance_data_handler import get_key_event_type, build_template_data
from .memory_assistance_enum import MemoryAssistanceAction, MemoryAssistanceState
from .memory_assistance_state_manager import get_init_state, get_next_state
from .memory_saving_retrieving_api import enable_memory_saving, search_texts_by_similarity, search_matching_images, \
    insert_image_memory, insert_text_memory

_logger = logging_utility.setup_logger(__name__)

_SPEECH_RECOGNITION_DELAY_MILLIS = MemoryAssistanceConfig.MEMORY_RECALL_SPEECH_PROCESS_DURATION_SECONDS * 1000
_IMAGE_SAMPLING_DURATION_MILLIS = MemoryAssistanceConfig.IMAGE_SAMPLING_DURATION_SECONDS * 1000
_RECALL_INSTANCES_COUNT = MemoryAssistanceConfig.MEMORY_RECALL_INSTANCES_COUNT

_MEMORY_KEY_SPEECH_DATA = "memory_service:speech_data"
_MEMORY_KEY_STATE = "memory_service:state"


class MemoryAssistanceService(BaseComponent):
    '''
    Memory Assistance Service to save and retrieve memories.
    '''

    SUPPORTED_DATATYPES = {
        "SPEECH_INPUT_DATA",
        "KEY_EVENT_DATA",
        "TEMPLATE_DATA",
    }

    def __init__(self, name):
        super().__init__(name)
        self.last_image_saved_millis = 0

        try:
            enable_memory_saving()
        except MilvusException:
            _logger.exception("Error in connecting to Milvus")
            sys.exit(1)  # Exit with status 1 to indicate an error

        super().set_memory_data(_MEMORY_KEY_SPEECH_DATA, "")
        super().set_memory_data(_MEMORY_KEY_STATE, get_init_state())

    def run(self, raw_data):
        '''
        Run the Memory Assistance Service.
        :param raw_data:

        Main processing will be done on the Camera data, which will be saved as an image memory along with the
        speech/text data.
        '''

        super().set_component_status(base_keys.COMPONENT_IS_RUNNING_STATUS)

        origin = raw_data[base_keys.ORIGIN_KEY]

        if origin == base_keys.CAMERA_WIDGET:  # image memory upload
            self._handle_camera_data(raw_data)

        if origin == base_keys.WHISPER_PROCESSOR:  # assume audio transcription is received
            self._handle_speech_data(raw_data[base_keys.AUDIO_TRANSCRIPTION_DATA])

        if origin == base_keys.WEBSOCKET_WIDGET:  # assume text is received
            self._handle_websocket_data(raw_data[base_keys.WEBSOCKET_DATATYPE], raw_data[base_keys.WEBSOCKET_MESSAGE])

        if origin == base_keys.KEYBOARD_WIDGET:
            self._handle_keyboard(raw_data[base_keys.KEYBOARD_EVENT], raw_data[base_keys.KEYBOARD_KEY_NAME],
                                  raw_data[base_keys.KEYBOARD_KEY_CODE])

    def _handle_camera_data(self, raw_data: dict) -> None:
        state = self.get_state()

        # Perform actions based on the current state
        if state == MemoryAssistanceState.MEMORY_SAVING_STATE:
            self._attempt_save_memory(raw_data[base_keys.CAMERA_FRAME])
        elif state == MemoryAssistanceState.MEMORY_RECALL_STATE:
            self._attempt_retrieve_memory()

            self.update_state(MemoryAssistanceAction.MEMORY_RECALL_END)

    def _attempt_save_memory(self, image_frame) -> bool:
        # Check time since last image save
        if time_utility.get_current_millis() - self.last_image_saved_millis < _IMAGE_SAMPLING_DURATION_MILLIS:
            return False

        image_saved = self._save_memory(image_frame)
        if image_saved:
            self.last_image_saved_millis = time_utility.get_current_millis()

        return image_saved

    def _save_memory(self, image_frame):
        try:
            insert_image_memory(image_frame)

            speech_text_data = self.pop_speech_in_memory().strip()
            if speech_text_data != "":
                insert_text_memory(speech_text_data)

            _logger.debug("Saved memory (image and speech, separately)")
            return True
        except MilvusException:
            _logger.exception("Error saving memory")
            return False

    def _attempt_retrieve_memory(self):
        speech_text_data = self.pop_speech_in_memory().strip()

        _logger.info("_attempt_retrieve_memory: speech: {speech}", speech=speech_text_data)
        _texts, _images = self._retrieve_memory(speech_text_data)

        most_similar_text = ""
        if len(_texts) > 0:
            most_similar_text = _texts[0]
        most_similar_image = []
        if len(_images) > 0:
            image_utility.save_image("temp.png", _images[0])
            most_similar_image = image_utility.get_png_image_bytes(_images[0])

        if len(most_similar_text) > 0 or len(most_similar_image) > 0:
            self._send_websocket_data(most_similar_text, most_similar_image)

    def _retrieve_memory(self, text: str) -> tuple:
        if text is None or text == "":
            return [], []

        _texts = search_texts_by_similarity(text, _RECALL_INSTANCES_COUNT)
        _images = search_matching_images(text, _RECALL_INSTANCES_COUNT)

        _logger.info("Recalled: {speech}, images = {count}", speech=";".join(_texts), count=len(_images))

        return _texts, _images

    def _handle_websocket_data(self, datatype, data) -> None:
        # Decode and process WebSocket data
        _logger.debug("Memory Service: {datatype}", datatype=datatype)
        decoded_data = datatypes_helper.convert_json_to_protobuf(datatype, data)
        if datatype == memory_keys.SPEECH_INPUT_DATA:
            voice = decoded_data.voice
            self._handle_speech_data(voice)

        if datatype == memory_keys.KEY_EVENT_DATA:
            self._handle_keyboard(get_key_event_type(decoded_data), decoded_data.name, decoded_data.code)

    def _handle_speech_data(self, voice: str) -> None:
        _logger.debug("Received speech data: {voice}", voice=voice)

        self.push_speech_in_memory(voice)

    def _handle_keyboard(self, key_event: str, key_name: str, key_code: int) -> None:
        if key_code == MemoryAssistanceConfig.MEMORY_RECALL_KEY_CODE:
            _logger.debug("Received keyboard input: {key_event}, {key_name}, {key_code}", key_event=key_event,
                          key_name=key_name, key_code=key_code)

            if key_event == base_keys.KEYBOARD_EVENT_PRESS:
                self.update_state(MemoryAssistanceAction.MEMORY_RECALL_START)
            if key_event == base_keys.KEYBOARD_EVENT_RELEASE:
                self.update_state(MemoryAssistanceAction.MEMORY_RECALL_END)

    def push_speech_in_memory(self, speech) -> None:
        '''
        Append the new speech data into memory
        :param speech: new speech
        '''
        old_speech = super().get_memory_data(_MEMORY_KEY_SPEECH_DATA)
        new_speech = old_speech + " " + speech

        super().set_memory_data(_MEMORY_KEY_SPEECH_DATA, new_speech)

    def pop_speech_in_memory(self) -> str:
        '''
        :return: the speech in memory after removing it from memory
        '''
        speech = super().get_memory_data(_MEMORY_KEY_SPEECH_DATA)
        # reset the memory after reading
        super().set_memory_data(_MEMORY_KEY_SPEECH_DATA, "")

        _logger.debug("Read speech data: {speech}", speech=speech)
        return speech

    def get_state(self) -> MemoryAssistanceState:
        # Get current state from memory
        return super().get_memory_data(_MEMORY_KEY_STATE)

    def update_state(self, action: MemoryAssistanceAction) -> None:
        # Get current state and update if needed
        state = self.get_state()
        new_state = get_next_state(state, action)

        if new_state != state:
            super().set_memory_data(_MEMORY_KEY_STATE, new_state)
            _logger.info("State updated to {new_state}", new_state=new_state)

    def _send_websocket_data(self, text: str = "", image: bytes = None) -> None:
        _logger.debug("Sending data to websocket clients: text: {text}", text=text)
        websocket_template_data = build_template_data(text=text, image=image)

        super().send_to_component(websocket_message=websocket_template_data)
