import json
import base_keys
from DataFormat import datatypes_helper
from Services.pandalens_service import (pandalens_keys,
                                        pandalens_db,
                                        pandalens_const,
                                        pandalens_blog,
                                        pandalens_data_handler,
                                        pandalens_state_manager)
from Utilities import logging_utility, image_utility, time_utility
from base_component import BaseComponent
from .pandalens_enum import PandaLensState, PandaLensAction
from .pandalens_llm import PandaLensAI

_logger = logging_utility.setup_logger(__name__)


class PandaLensService(BaseComponent):
    """
    Handles the main logic for the PandaLens service, which includes processing data from the camera and user input.
    """

    def __init__(self, name):
        super().__init__(name)
        self.pandalens_ai = PandaLensAI()
        self.state = pandalens_state_manager.get_init_state()
        self.previous_llm_invoke_time = time_utility.get_current_millis()
        self.image_of_interest = None

    def run(self, raw_data):
        super().set_component_status(base_keys.COMPONENT_IS_RUNNING_STATUS)

        origin = raw_data[base_keys.ORIGIN_KEY]

        if origin == base_keys.CAMERA_WIDGET:
            self._store_camera_data_in_memory(raw_data)

        if origin == base_keys.WEBSOCKET_WIDGET:
            datatype = raw_data[base_keys.WEBSOCKET_DATATYPE]
            data = raw_data[base_keys.WEBSOCKET_MESSAGE]
            data = datatypes_helper.convert_json_to_protobuf(datatype, data)
            self._handle_websocket_data(datatype, data)

    def _store_camera_data_in_memory(self, raw_data):
        super().set_memory_data(base_keys.CAMERA_FRAME, raw_data[base_keys.CAMERA_FRAME])
        super().set_memory_data(base_keys.CAMERA_FRAME_WIDTH, raw_data[base_keys.CAMERA_FRAME_WIDTH])
        super().set_memory_data(base_keys.CAMERA_FRAME_HEIGHT, raw_data[base_keys.CAMERA_FRAME_HEIGHT])

    def _send_websocket_pandalens_question(self, image, text_content="", speech_content=""):
        image_base_64 = self.array_to_base64(image)
        websocket_pandalens_data = pandalens_data_handler.build_pandalens_question(image_base_64, text_content,
                                                                                   speech_content)
        super().send_to_component(websocket_message=websocket_pandalens_data,
                                  websocket_client_type=base_keys.UNITY_CLIENT)

    def _send_websocket_pandalens_response(self, text_content="", speech_content=""):
        websocket_pandalens_data = pandalens_data_handler.build_pandalens_response(text_content, speech_content)
        super().send_to_component(websocket_message=websocket_pandalens_data,
                                  websocket_client_type=base_keys.UNITY_CLIENT)

    def _send_websocket_pandalens_moments(self, moments=None):
        if moments is None:
            moments = []
        websocket_pandalens_data = pandalens_data_handler.build_pandalens_moments(moments)
        super().send_to_component(websocket_message=websocket_pandalens_data,
                                  websocket_client_type=base_keys.UNITY_CLIENT)

    def _send_websocket_pandalens_error(self, speech):
        websocket_pandalens_data = pandalens_data_handler.build_pandalens_error(speech)
        super().send_to_component(websocket_message=websocket_pandalens_data,
                                  websocket_client_type=base_keys.UNITY_CLIENT)

    def _send_websocket_pandalens_reset(self, ui_display):
        websocket_pandalens_data = pandalens_data_handler.build_pandalens_reset(ui_display)
        super().send_to_component(websocket_message=websocket_pandalens_data,
                                  websocket_client_type=base_keys.UNITY_CLIENT)

    def _handle_websocket_data(self, socket_data_type, decoded_data):
        if socket_data_type == pandalens_keys.FINGER_POINTING_DATA:
            self._handle_point_select(decoded_data)
        elif socket_data_type == pandalens_keys.GAZE_POINTING_DATA:
            self._handle_point_select(decoded_data)
        elif socket_data_type == pandalens_keys.SPEECH_INPUT_DATA:
            self._handle_speech(decoded_data)
        elif socket_data_type == pandalens_keys.PANDALENS_EVENT_DATA:
            self._handle_key_events(decoded_data)
        else:
            _logger.error("Unknown websocket type {type} received in Pandalens Service", type=socket_data_type)
            return

    def _update_state(self, client_action):
        next_state = pandalens_state_manager.get_next_state(self.state, client_action)
        if self.state is next_state:
            return False
        self.state = next_state
        return True

    def _reset_state(self):
        self.pandalens_ai.clear_chat_history()
        self.state = pandalens_state_manager.reset()

    def _handle_key_events(self, decoded_data):
        key = decoded_data.key_input
        if key == pandalens_const.CAMERA_INPUT_EVENT_KEY:
            self._on_cam_key_press()
        elif key == pandalens_const.IDLE_INPUT_EVENT_KEY:
            self._reset_state()
        elif key == pandalens_const.SUMMARY_INPUT_KEY:
            self._on_summary_key_press()

    def _on_summary_key_press(self):
        if not self._update_state(PandaLensAction.CLIENT_SUMMARY_PRESS):
            return
        json_moments = pandalens_db.get_all_moments()
        moment_summaries = []
        for moment in json_moments:
            moment_summaries.append(moment[pandalens_const.DB_MOMENT_SUMMARY_KEY])
        self._send_websocket_pandalens_moments(moment_summaries)

    def _on_cam_key_press(self):
        # Prevent unnecessary cost of querying LLM
        if not self._update_state(PandaLensAction.CLIENT_CAMERA_PRESS):
            return
        frame, _, _ = self._get_latest_frame_from_memory()
        self.image_of_interest = frame

        self._generate_send_question(cropped_image=self.image_of_interest,
                                     user_action=pandalens_const.CAMERA_ACTION_FOR_LLM)

    def _handle_point_select(self, point_data):
        # Prevent unnecessary cost of querying LLM
        curr_time = time_utility.get_current_millis()
        if curr_time - self.previous_llm_invoke_time < pandalens_const.POINTER_LLM_INVOKE_COOLDOWN_MILLIS:
            return
        if not self._update_state(PandaLensAction.CLIENT_INTEREST):
            return

        frame, frame_width, frame_height = self._get_latest_frame_from_memory()
        self.image_of_interest = frame

        # identify object data and send it to the client
        cropped_image = self._get_cropped_image_around_pointer(point_data, frame, frame_width, frame_height)

        self._generate_send_question(cropped_image=cropped_image,
                                     user_action=pandalens_const.POINTER_INTEREST_ACTION_FOR_LLM)

    def _handle_speech(self, speech_data):
        speech = speech_data.voice
        if self.state is PandaLensState.SERVER_QNA_STATE:
            self._generate_send_response(speech)
        elif self.state is PandaLensState.SERVER_BLOGGING_STATE:
            self._generate_save_summary(speech)

    def _generate_send_response(self, speech):
        question, summary = self.pandalens_ai.get_subsequent_generated_response(speech)
        self.previous_llm_invoke_time = time_utility.get_current_millis()

        if question == pandalens_const.LLM_NO_QUESTIONS:
            pandalens_db.save_moment(summary, self.image_of_interest)
            self._reset_state()
            self._send_websocket_pandalens_reset("Moment has been saved.")
            return

        self._send_websocket_pandalens_response(question, question)

    def _generate_send_question(self, cropped_image, user_action):
        question, summary = self.pandalens_ai.get_first_generated_response(cropped_image, user_action)
        self.previous_llm_invoke_time = time_utility.get_current_millis()

        if question == pandalens_const.LLM_NO_QUESTIONS:
            pandalens_db.save_moment(summary, self.image_of_interest)
            self._reset_state()
            self._send_websocket_pandalens_reset("Moment has been saved.")
            return

        self._send_websocket_pandalens_question(self.image_of_interest, question, question)

    def _generate_save_summary(self, speech_data):
        json_moments = pandalens_db.get_all_moments()
        if len(json_moments) == 0:
            self._send_websocket_pandalens_error(pandalens_const.MOMENT_LIST_EMPTY_MESSAGE)
            return
        intro, conclusion = self.pandalens_ai.generate_intro_conclusion(speech_data, json.dumps(json_moments))
        pandalens_blog.create_blog_in_word(intro, conclusion, json_moments)
        pandalens_db.delete_all_moments()
        self._reset_state()
        self._send_websocket_pandalens_reset("Blog has been generated and saved in the cloud!")

    def _get_latest_frame_from_memory(self):
        frame = super().get_memory_data(base_keys.CAMERA_FRAME)
        frame_width = super().get_memory_data(base_keys.CAMERA_FRAME_WIDTH)
        frame_height = super().get_memory_data(base_keys.CAMERA_FRAME_HEIGHT)

        return frame, frame_width, frame_height

    def _get_cropped_image_around_pointer(self, point_data, frame, frame_width, frame_height):
        image_of_interest = frame

        pointing_region = self._get_image_region_from_camera(point_data.camera_x,
                                                             point_data.camera_y,
                                                             frame_width, frame_height,
                                                             pandalens_const.POINTING_LOCATION_OFFSET_PERCENTAGE)

        image_of_interest_clamped = image_utility.get_cropped_frame(image_of_interest, pointing_region[0],
                                                                    pointing_region[1],
                                                                    pointing_region[2], pointing_region[3])

        return image_of_interest_clamped

    def _get_most_prominent_object(self, objects_of_interest):
        object_of_interest = None
        if len(objects_of_interest) > 0:
            object_of_interest = objects_of_interest[0]
            _logger.debug("Object of interest: {object_of_interest}", object_of_interest=object_of_interest)

        return object_of_interest

    def _get_image_region_from_camera(self, camera_x, camera_y, image_width, image_height, offset_length,
                                      camera_calibration=None):
        relative_x = camera_x
        relative_y = camera_y
        # FIXME: use camera calibration (instead of hard coded values for HL2), Add the calibration values to Camera
        if camera_calibration:
            relative_x = (relative_x + 0.18) / (0.20 + 0.18)
            relative_y = (relative_y - 0.1) / (-0.12 - 0.1)
        else:
            relative_x = max(0, min(camera_x, 1))
            relative_y = max(0, min(camera_y, 1))

        image_x = int(relative_x * image_width)
        image_y = int(relative_y * image_height)
        image_offset = int(offset_length * image_width / 2)
        image_region = [self._clamp_image(image_x - image_offset, image_width),
                        self._clamp_image(image_y - image_offset, image_height),
                        self._clamp_image(image_x + image_offset, image_width),
                        self._clamp_image(image_y + image_offset, image_height)]
        return image_region

    def _clamp_image(self, actual, max_value):
        return max(0, min(actual, max_value - 1))

    def array_to_base64(self, image_array):
        # to bytes
        image_png_bytes = image_utility.get_png_image_bytes(image_array)
        # Encode to base64
        img_base64 = image_utility.get_base64_image(image_png_bytes)
        return img_base64
