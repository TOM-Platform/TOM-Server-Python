from typing import Union, Any, Optional

import base_keys
from DataFormat import datatypes_helper
from Services.pandalens_service import (pandalens_keys,
                                        pandalens_db,
                                        pandalens_const,
                                        pandalens_blog,
                                        pandalens_data_handler,
                                        pandalens_state_manager)
from User.UserProfileManager import UserProfileManager
from Utilities import logging_utility, image_utility, time_utility, camera_utility, file_utility
from base_component import BaseComponent
from .pandalens_enum import PandaLensState, PandaLensAction
from .pandalens_llm import PandaLensAI

_logger = logging_utility.setup_logger(__name__)


class PandaLensService(BaseComponent):
    """
    Handles the main logic for the PandaLens service, which includes processing data from the camera and user input.
    """

    SUPPORTED_DATATYPES = {
        "FINGER_POINTING_DATA",
        "SPEECH_INPUT_DATA",
        "GAZE_POINTING_DATA",
        "PANDALENS_EVENT_DATA",
        "PANDALENS_QUESTION",
        "PANDALENS_RESPONSE",
        "PANDALENS_MOMENTS",
        "PANDALENS_ERROR",
        "PANDALENS_RESET"
    }

    def __init__(self, name):
        super().__init__(name)

        self.state = pandalens_state_manager.get_init_state()

        self.pandalens_ai = PandaLensAI()
        self.previous_llm_invoke_time = time_utility.get_current_millis()

        self.moment_image_frame = None
        self.moment_identifier = None
        self.moment_summary = None

        self.last_location = None
        self.last_location_update_time = 0

        self.user_profile = None

        self.load_user_profile()

    def run(self, raw_data):
        super().set_component_status(base_keys.COMPONENT_IS_RUNNING_STATUS)

        origin = raw_data[base_keys.ORIGIN_KEY]

        if origin == base_keys.CAMERA_WIDGET:
            self._store_camera_frame_in_memory(raw_data)

        if origin == base_keys.WEBSOCKET_WIDGET:
            datatype = raw_data[base_keys.WEBSOCKET_DATATYPE]
            data = raw_data[base_keys.WEBSOCKET_MESSAGE]
            data = datatypes_helper.convert_json_to_protobuf(datatype, data)
            self._handle_websocket_data(datatype, data)

    def _store_camera_frame_in_memory(self, raw_data):
        frame = raw_data.get(base_keys.CAMERA_FRAME)
        if frame is None or frame.size == 0:
            _logger.warning("Empty or missing camera frame; skipping storage.")
            return

        super().set_memory_data(base_keys.CAMERA_FRAME, frame)
        super().set_memory_data(base_keys.CAMERA_FRAME_WIDTH, raw_data[base_keys.CAMERA_FRAME_WIDTH])
        super().set_memory_data(base_keys.CAMERA_FRAME_HEIGHT, raw_data[base_keys.CAMERA_FRAME_HEIGHT])

    def _get_latest_camera_frame_from_memory(self):
        _logger.debug("Getting latest camera frame from memory")
        try:
            frame = super().get_memory_data(base_keys.CAMERA_FRAME)
        except KeyError:
            _logger.debug("No camera frame key in memory.")
            return None, None, None
        except Exception as e:
            _logger.error("Error retrieving camera frame from memory: {e}", e=e)
            return None, None, None

        if frame is None or frame.size == 0:
            _logger.debug("Stored camera frame is empty.")
            return None, None, None

        width = super().get_memory_data(base_keys.CAMERA_FRAME_WIDTH)
        height = super().get_memory_data(base_keys.CAMERA_FRAME_HEIGHT)
        return frame, width, height

    def _send_websocket_pandalens_question(self, image_frame, text_content="", speech_content="", icon="",
                                           show_image=False):
        image_base_64 = self.array_to_base64(image_frame)
        websocket_pandalens_data = pandalens_data_handler.build_pandalens_question(image_base_64, text_content,
                                                                                   speech_content, icon, show_image)
        super().send_to_component(websocket_message=websocket_pandalens_data,
                                  websocket_client_type=base_keys.UNITY_CLIENT)

    def _send_websocket_pandalens_moments(self, title, moments, speech=""):
        if moments is None:
            moments = []
        websocket_pandalens_data = pandalens_data_handler.build_pandalens_moments(title, moments, speech)
        super().send_to_component(websocket_message=websocket_pandalens_data,
                                  websocket_client_type=base_keys.UNITY_CLIENT)

    def _send_websocket_pandalens_error(self, error, text="", audio="", duration_seconds=5):
        websocket_pandalens_data = pandalens_data_handler.build_pandalens_error(error, text, audio, duration_seconds)
        super().send_to_component(websocket_message=websocket_pandalens_data,
                                  websocket_client_type=base_keys.UNITY_CLIENT)

    def _send_websocket_pandalens_reset(self, message, audio="", duration_seconds=0):
        websocket_pandalens_data = pandalens_data_handler.build_pandalens_reset(message, audio, duration_seconds)
        super().send_to_component(websocket_message=websocket_pandalens_data,
                                  websocket_client_type=base_keys.UNITY_CLIENT)

    def _handle_websocket_data(self, socket_data_type, decoded_data):
        if socket_data_type == pandalens_keys.FINGER_POINTING_DATA:
            _logger.debug("[RX] Websocket: Hand")
            self._handle_point_select(decoded_data)
        elif socket_data_type == pandalens_keys.GAZE_POINTING_DATA:
            _logger.debug("[RX] Websocket: Gaze")
            self._handle_point_select(decoded_data)
        elif socket_data_type == pandalens_keys.SPEECH_INPUT_DATA:
            _logger.debug("[RX] Websocket: Speech= {speech}", speech=decoded_data.voice)
            self._handle_speech(decoded_data)
        elif socket_data_type == pandalens_keys.PANDALENS_EVENT_DATA:
            _logger.debug("[RX] Websocket: Event")
            self._handle_key_events(decoded_data)
        else:
            _logger.error("[RX] Unknown Websocket type: {type}", type=socket_data_type)
            return

    def _attempt_to_update_state(self, client_action):
        next_state = pandalens_state_manager.get_next_state(self.state, client_action)
        if self.state is next_state:
            return False
        self.state = next_state
        _logger.debug("State updated to {state}", state=self.state)
        return True

    def _reset_state(self):
        self.moment_identifier = None
        self.moment_summary = None

        self.moment_image_frame = None

        self.pandalens_ai.clear_chat_history()
        self.state = pandalens_state_manager.get_init_state()

    def _handle_key_events(self, decoded_data):
        key = decoded_data.key_input
        if key == pandalens_const.CAMERA_INPUT_EVENT_KEY:
            self._on_cam_key_press()
        elif key == pandalens_const.IDLE_INPUT_EVENT_KEY:
            self._on_cancel_key_press()
        elif key == pandalens_const.SUMMARY_INPUT_KEY:
            self._on_summary_key_press()

    def _on_summary_key_press(self):
        _logger.debug("Summary Button Pressed")
        if not self._attempt_to_update_state(PandaLensAction.CLIENT_SUMMARY_PRESS):
            return

        json_moments = pandalens_db.get_all_moments()

        if len(json_moments) == 0:
            self._reset_state()
            self._send_websocket_pandalens_reset(pandalens_const.MESSAGE_MOMENT_LIST_EMPTY_TEXT,
                                                 pandalens_const.MESSAGE_MOMENT_LIST_EMPTY_AUDIO,
                                                 pandalens_const.MESSAGE_MOMENT_LIST_EMPTY_DURATION_SECONDS)
            return

        moment_summaries = []
        moment_index = 1
        for moment in json_moments:
            # use the identifiers instead of actual summaries
            moment_summaries.append(f"{moment_index:2d}. {moment[pandalens_const.DB_MOMENT_IDENTIFIER_KEY]}")
            moment_index += 1

        _logger.debug("Moments:: {moment_summaries}", moment_summaries=str(moment_summaries))

        self._send_websocket_pandalens_moments(pandalens_const.MESSAGE_MOMENTS_SUMMARY_TEXT, moment_summaries,
                                               pandalens_const.MESSAGE_MOMENTS_SUMMARY_TEXT_AUDIO)

    def _on_cam_key_press(self):
        _logger.debug("Camera Button Pressed")
        # Prevent unnecessary cost of querying LLM
        if not self._attempt_to_update_state(PandaLensAction.CLIENT_INTEREST_CAMERA_PRESS):
            return

        frame, _, _ = self._get_latest_camera_frame_from_memory()
        self.moment_image_frame = frame

        self._generate_and_send_response(cropped_image=frame, user_action=pandalens_const.CAMERA_ACTION_FOR_LLM)

    def _on_cancel_key_press(self):
        _logger.debug("Cancel Button Pressed")
        if self.state is PandaLensState.SERVER_QA_STATE_USER_INITIATE:  # save the moment
            if self.moment_summary is None and self.moment_image_frame is not None:
                self.moment_identifier, self.moment_summary, _, _ = self._generate_identifier_summary_answer_question(
                    cropped_image=self.moment_image_frame)

            pandalens_db.save_moment(self.moment_identifier, self.moment_summary, self.moment_image_frame)
        if self.state is PandaLensState.SERVER_QA_STATE_SYSTEM_INITIATE:
            pass  # do not save the moment

        self._reset_state()

    def _handle_point_select(self, point_data):
        # Prevent unnecessary cost of querying LLM
        curr_time = time_utility.get_current_millis()
        if curr_time - self.previous_llm_invoke_time < pandalens_const.AI_INTEREST_DETECT_LLM_INVOKE_COOLDOWN_MILLIS:
            return

        if not self._attempt_to_update_state(PandaLensAction.CLIENT_INTEREST_SYSTEM_DETECT):
            return

        frame, frame_width, frame_height = self._get_latest_camera_frame_from_memory()
        self.moment_image_frame = frame

        # identify object data and send it to the client
        cropped_image = self._get_cropped_image_around_pointer(point_data, frame, frame_width, frame_height)

        self._generate_and_send_response(cropped_image=cropped_image,
                                         user_action=pandalens_const.POINTER_INTEREST_ACTION_FOR_LLM)

    def _handle_speech(self, speech_data):
        speech = speech_data.voice

        self._attempt_to_update_state(PandaLensAction.CLIENT_INTEREST_USER_SPEAK)

        if self.state is PandaLensState.SERVER_QA_STATE_USER_INITIATE:
            self._generate_and_send_response(cropped_image=self.moment_image_frame, user_utterance=speech)
        elif self.state is PandaLensState.SERVER_BLOGGING_STATE:
            self._generate_and_save_blog(speech)

    def _get_notification_icon_and_visibility(self):
        """
        Get the icon and visibility for the notification based on the current state.
        :return: icon, show_icon
        """
        if self.state is PandaLensState.SERVER_QA_STATE_USER_INITIATE:
            icon = pandalens_const.INTEREST_DETECT_ICON_MANUAL
            show_icon = False
        elif self.state is PandaLensState.SERVER_QA_STATE_SYSTEM_INITIATE:
            icon = pandalens_const.INTEREST_DETECT_ICON_GAZE
            show_icon = True
        else:
            icon = pandalens_const.INTEREST_DETECT_ICON_MANUAL
            show_icon = True

        return icon, show_icon

    def _generate_and_send_response(self, cropped_image, user_action=None, user_utterance=None):
        self.previous_llm_invoke_time = time_utility.get_current_millis()
        identifier, summary, user_answer, system_question = self._generate_identifier_summary_answer_question(
            cropped_image, user_action, user_utterance)
        self.moment_identifier = identifier
        self.moment_summary = summary
        self._send_response(cropped_image, user_answer, system_question, identifier, summary)

    def _generate_identifier_summary_answer_question(self, cropped_image, user_action=None, user_utterance=None):
        if cropped_image is not None:  # TODO: Remove this, which temporary save the image
            image_utility.save_image_bytes('temp.png', image_utility.get_jpg_image_bytes(cropped_image))

        location = self._get_current_location()
        time = self._get_current_time()
        user_profile = self.user_profile.to_dict()
        identifier, summary, user_answer, system_question = self.pandalens_ai.generate_moment_response(cropped_image,
                                                                                                       user_action,
                                                                                                       user_utterance,
                                                                                                       location, time,
                                                                                                       user_profile)

        return identifier, summary, user_answer, system_question

    def _send_response(
            self,
            cropped_image: Union[bytes, Any],  # e.g. numpy array or raw bytes
            user_answer: Optional[str],
            system_question: Optional[str],
            identifier: str,
            summary: str
    ) -> None:
        """
        Handle either saving the moment (no follow-up -> reset) or sending a follow-up question via WebSocket.
        """
        # normalize inputs
        user_answer = (user_answer or "").strip()
        system_question = (system_question or "").strip()
        default_question = pandalens_const.LLM_DEFAULT_QUESTION

        # --- save & reset branch ---
        if not system_question and not user_answer:
            _logger.debug("No follow-up required: saving moment {identifier} and resetting state.",
                          identifier=identifier)
            pandalens_db.save_moment(identifier, summary, cropped_image)
            self._reset_state()
            self._send_websocket_pandalens_reset("")
            return

        # Use user_answer if available, otherwise system_question
        text_content = user_answer if user_answer else system_question
        # only play speech if it's more than just the default question
        speech_content = text_content if text_content and text_content != default_question else ""
        # select icon
        icon, show_icon = self._get_notification_icon_and_visibility()

        _logger.debug("Moment response: text:{text}, speech: {audio}, icon: {icon}, show_icon: {show_icon}",
                      text=text_content, audio=speech_content, icon=icon, show_icon=show_icon)
        self._send_websocket_pandalens_question(cropped_image, text_content, speech_content, icon, not show_icon)

    def _generate_and_save_blog(self, speech_data):
        json_moments = pandalens_db.get_all_moments()
        if len(json_moments) == 0:
            self._send_websocket_pandalens_error(pandalens_const.ERROR_MOMENT_LIST_EMPTY,
                                                 pandalens_const.MESSAGE_MOMENT_LIST_EMPTY_TEXT,
                                                 pandalens_const.MESSAGE_MOMENT_LIST_EMPTY_AUDIO,
                                                 pandalens_const.MESSAGE_MOMENT_LIST_EMPTY_DURATION_SECONDS)
            return

        self.previous_llm_invoke_time = time_utility.get_current_millis()

        moment_count = len(json_moments)
        for moment_index in range(moment_count):
            moment = json_moments[moment_index]
            moment.pop('id', None)  # Remove 'id' if it exists
            moment = {'index': moment_index + 1, **moment}  # Insert 'index' first which starts from 1
            json_moments[moment_index] = moment

        # Get enhanced blog content after filtering by LLM
        indexes, enhanced_summaries, introduction, conclusion = (
            self.pandalens_ai.generate_summaries_introduction_conclusion(
                json_moments,
                speech_data,
                self.user_profile.to_dict()
            ))

        # Selected moments (1-based 'indexes' converted to 0-based index)
        filtered_moments = [json_moments[i - 1] for i in indexes if 1 <= i <= moment_count]
        # Ignored moments (i is 0-based; i+1 is the 1-based index)
        ignored_moments = [json_moments[i] for i in range(moment_count) if (i + 1) not in indexes]

        # Create blog with enhanced summaries
        pandalens_blog.create_blog_in_word(
            introduction,
            conclusion,
            filtered_moments,
            enhanced_summaries,
            ignored_moments
        )

        pandalens_db.delete_all_moments()

        self._reset_state()

        self._send_websocket_pandalens_reset(self.get_moment_generated_display_text(indexes, moment_count),
                                             pandalens_const.MESSAGE_BLOG_GENERATED_AUDIO,
                                             pandalens_const.MESSAGE_BLOG_GENERATED_DURATION_SECONDS)

    def get_moment_generated_display_text(self, indexes, moment_count):
        selected_moment_text = pandalens_const.MESSAGE_BLOG_GENERATED_TEXT + "\n\n Selected Moments: "
        if moment_count > len(indexes):
            selected_moment_text = selected_moment_text + str(indexes)
        else:
            selected_moment_text = selected_moment_text + "All"
        return selected_moment_text

    def _get_cropped_image_around_pointer(self, point_data, frame, frame_width, frame_height):
        calibrate_for_hololens = frame_width == 1280 and frame_height == 720
        pointing_region = camera_utility.get_image_region(point_data.camera_x,
                                                          point_data.camera_y,
                                                          frame_width,
                                                          frame_height,
                                                          pandalens_const.POINTING_LOCATION_OFFSET_PERCENTAGE,
                                                          calibrate_for_hololens)
        _logger.debug("Cropped image region: {region}", region=pointing_region)

        image_of_interest_clamped = image_utility.get_cropped_frame(frame,
                                                                    pointing_region[0],
                                                                    pointing_region[1],
                                                                    pointing_region[2],
                                                                    pointing_region[3])

        return image_of_interest_clamped

    def array_to_base64(self, image_array: bytes) -> str:
        """
        :return: empty if image_array is empty
        """
        if image_array is None or len(image_array) == 0:
            _logger.warning('Empty image array')
            return ""

        # to bytes
        image_png_bytes = image_utility.get_png_image_bytes(image_array)
        # Encode to base64
        img_base64 = image_utility.get_base64_image(image_png_bytes)
        return img_base64

    def _get_current_location(self) -> dict:
        if (time_utility.get_current_millis() - self.last_location_update_time
                < pandalens_const.LOCATION_QUERY_MINIMUM_MILLIS):
            return self.last_location

        self.last_location_update_time = time_utility.get_current_millis()
        self.last_location = pandalens_data_handler.get_current_location()
        _logger.debug("Location: {location}", location=self.last_location)

        return self.last_location

    def _get_current_time(self) -> str:
        return time_utility.get_time_string(pandalens_const.DATE_TIME_FORMAT)

    def load_user_profile(self):
        _logger.debug("Loading User Profile ...")
        profile_folder = file_utility.get_path_from_project_root(
            pandalens_const.SEQUENCE_PATH_TO_PROFILES_FROM_PROJECT_ROOT)
        profile_path = file_utility.get_path_with_filename(profile_folder,
                                                           pandalens_const.DEFAULT_USER_PROFILE_NAME)
        _logger.debug("User Profile: {profile_path}", profile_path=profile_path)

        user_profile_manager = UserProfileManager(profile_path)

        self.user_profile = user_profile_manager.load_profile()
