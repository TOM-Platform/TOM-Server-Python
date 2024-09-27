# coding: utf-8

import statistics

import base_keys
from APIs.langchain_llm.langchain_openai import OpenAIClient
from DataFormat import datatypes_helper
from Utilities import image_utility, logging_utility, time_utility
from base_component import BaseComponent
from . import learning_display, learning_keys
from .learning_data_handler import build_highlight_point_data, build_learning_data
from .learning_service_config import LearningConfig

_logger = logging_utility.setup_logger(__name__)


class LearningService(BaseComponent):
    '''
    This class is responsible for handling the learning service that extends from BaseComponent
    '''

    def __init__(self, name):
        super().__init__(name)
        self.text_generator = OpenAIClient()
        self.learning_map = {}
        self.text_detection_sent_time = 0
        self.learning_data_sent_time = 0
        self.learning_data_has_sent = False
        self.learning_data_display_duration = LearningConfig.MIN_LEARNING_CONTENT_DISPLAY_DURATION_MILLIS
        self.finger_pose_buffer = []
        self.last_point = None
        self.last_frame = None

    def run(self, raw_data: dict):
        '''
        This function is responsible for running the learning service
        Parameters:
        ________
        raw_data: dict
        '''
        super().set_component_status(base_keys.COMPONENT_IS_RUNNING_STATUS)
        origin = raw_data[base_keys.ORIGIN_KEY]
        if origin == base_keys.CAMERA_WIDGET:
            # set the camera data frame
            self._handle_camera_data(raw_data)
        if origin == base_keys.WEBSOCKET_WIDGET:
            datatype = raw_data[base_keys.WEBSOCKET_DATATYPE]
            data = raw_data[base_keys.WEBSOCKET_MESSAGE]
            # FIXME: remove this conversion once all components are using protobuf and use object values
            data = datatypes_helper.convert_json_to_protobuf(datatype, data)
            _logger.debug("Learning Service: {datatype}", datatype=datatype)
            self._handle_websocket_data(datatype, data)

    def _send_websocket_learning_data(self, object_of_interest: str, text_content: str, speech_content: str):
        websocket_learning_data = build_learning_data(
            object_of_interest,
            text_content,
            speech_content
        )
        super().send_to_component(websocket_message=websocket_learning_data)

    def _send_websocket_highlight_point_data(self, x: float, y: float, z: float, details: str = ""):
        websocket_highlight_point_data = build_highlight_point_data(x, y, z, details)
        super().send_to_component(websocket_message=websocket_highlight_point_data)

    def _handle_camera_data(self, raw_data):
        super().set_memory_data(base_keys.CAMERA_FRAME, raw_data[base_keys.CAMERA_FRAME])
        super().set_memory_data(base_keys.CAMERA_FRAME_WIDTH, raw_data[base_keys.CAMERA_FRAME_WIDTH])
        super().set_memory_data(base_keys.CAMERA_FRAME_HEIGHT, raw_data[base_keys.CAMERA_FRAME_HEIGHT])

    def _handle_websocket_data(self, socket_data_type, decoded_data):
        if socket_data_type == learning_keys.REQUEST_LEARNING_DATA:
            self._handle_learning_request()
        elif socket_data_type == learning_keys.FINGER_POINTING_DATA:
            self._handle_finger_pose(decoded_data)
        elif socket_data_type == learning_keys.GAZE_POINTING_DATA:
            self._handle_gaze_point(decoded_data)
        elif socket_data_type == learning_keys.SPEECH_INPUT_DATA:
            self._handle_speech_data(decoded_data)
        else:
            _logger.error("Unknown websocket type {type} received in Learning Service", type=socket_data_type)

    def get_learning_content(self, question: str, image_frame=None) -> str:
        '''
        This function generates the learning content based on the object of interest, text content and speech content
        Parameters:
        ________
        question: str
            The user question
        '''
        prompt = f"{question}. Provide only the answer in one sentence."
        _logger.debug("Prompt: {prompt}", prompt=prompt)

        learning_content = ""
        try:
            frame = image_frame
            frame_width, frame_height = self.get_original_image_size()

            # use the last frame if the current frame is not available
            if frame is None and self.last_frame is not None:
                frame = self.last_frame

            # get the cropped image based on the last pointing location
            if self.last_point is not None:
                frame = self._get_cropped_from_camera(self.last_point, frame, frame_width, frame_height)

            if frame is None:
                learning_content = self.text_generator.generate(prompt)
            else:
                # always take in context of frame
                image_png_bytes = image_utility.get_png_image_bytes(frame)
                learning_content = self.text_generator.generate(prompt, image_png_bytes)
                # temporary save the image
                image_utility.save_image_bytes('temp.png', image_png_bytes)
        except Exception:
            _logger.exception("Error in text generation")

        return learning_content

    def get_original_image_size(self) -> tuple:
        '''
        This function gets the original image size
        :return: {tuple} frame_width, frame_height
        '''
        frame_width = super().get_memory_data(base_keys.CAMERA_FRAME_WIDTH)
        frame_height = super().get_memory_data(base_keys.CAMERA_FRAME_HEIGHT)
        return frame_width, frame_height

    def _handle_learning_request(self):
        _logger.debug("Received learning request")
        # FIXME: ideally send data based on the request
        self._clear_learning_data()

    def _handle_finger_pose(self, finger_pose_data):
        # see whether the pose if pointing to an object for a certain duration based on history
        if len(self.finger_pose_buffer) >= LearningConfig.FINGER_POINTING_BUFFER_SIZE:
            prev_avg_camera_x = statistics.mean([_data.camera_x for _data in self.finger_pose_buffer])
            prev_avg_camera_y = statistics.mean([_data.camera_y for _data in self.finger_pose_buffer])

            _logger.debug("Current:: x: {x}, y: {y}, Previous (avg):: x: {avg_x}, y: {avg_y}",
                          x=finger_pose_data.camera_x,
                          y=finger_pose_data.camera_y,
                          avg_x=prev_avg_camera_x,
                          avg_y=prev_avg_camera_y)

            # remove the oldest data
            self.finger_pose_buffer.pop(0)

            # if same location, identify object data and send it to the client
            if self.same_pointing_location(prev_avg_camera_x, prev_avg_camera_y, finger_pose_data,
                                           LearningConfig.POINTING_LOCATION_OFFSET_PERCENTAGE):
                self._handle_point_select(finger_pose_data)

        # temporary store finger pose data
        self.finger_pose_buffer.append(finger_pose_data)

    def _handle_gaze_point(self, gaze_point_data):
        self._handle_point_select(gaze_point_data)

    # gaze/gesture interaction
    def _handle_point_select(self, point_data):
        frame = super().get_memory_data(base_keys.CAMERA_FRAME)

        # notify the selection
        self._send_websocket_highlight_point_data(point_data.world_x, point_data.world_y, point_data.world_z)
        # update the selection
        self.last_point = point_data
        self.last_frame = frame
        # send the learning data
        question = "Briefly describe what you see. Ignore hands. If there is any text, please include them."
        self._send_learning_data(question, is_gaze_interaction=True, image_frame=frame)

    # voice interaction
    def _handle_speech_data(self, speech_data):
        voice = speech_data.voice
        _logger.info("Received speech data: {voice}", voice=voice)

        if voice is not None and voice != "":
            self._send_learning_data(voice)

    def _send_learning_data(self, question: str, is_gaze_interaction: bool = False, image_frame=None):
        self.learning_data_has_sent = True

        learning_content = self.get_learning_content(question, image_frame)
        _logger.info("Learning content: {content}", content=learning_content)

        # speak only for non-gaze interactions
        speak = ""
        if not is_gaze_interaction:
            speak = learning_content

        formatted_content = learning_display.get_formatted_learning_details(learning_content)
        self._send_websocket_learning_data("", formatted_content, speak)
        self.learning_data_display_duration = learning_display.get_content_showing_millis(learning_content)
        _logger.debug("Learning display duration: {duration}", duration=self.learning_data_display_duration)

        self.learning_data_sent_time = time_utility.get_current_millis()

    def _clear_learning_data(self):
        if (not self.learning_data_has_sent
                or time_utility.get_current_millis() - self.learning_data_sent_time
                < self.learning_data_display_duration):
            return

        self.learning_data_sent_time = time_utility.get_current_millis()
        self.learning_data_has_sent = False
        self.last_point = None
        self.last_frame = None
        self._send_websocket_learning_data("", "", "")

    def same_pointing_location(self, camera_x: float, camera_y: float, finger_pose_data, offset: float):
        '''
        This function checks whether the camera and finger pointing
        locations are the same
        Parameters:
        ________
        camera_x: float
            The camera x location
        camera_y: float
            The camera y location
        finger_pose_data: highlight_point_data_pb2.HighlightPointData
            The finger pose data
        offset: float
            The offset
        '''

        # FIXME: check if the data is valid
        if self.learning_data_has_sent:
            _logger.warn("Skip point checking")
            return False

        finger_x = finger_pose_data.camera_x
        finger_y = finger_pose_data.camera_y
        return abs(camera_x - finger_x) < offset and abs(camera_y - finger_y) < offset

    def _get_cropped_from_camera(self, point_data, frame, frame_width, frame_height):
        is_hololens = frame_width == 1280 and frame_height == 720
        finger_pointing_region = self._get_image_region_from_camera(
            point_data.camera_x,
            point_data.camera_y,
            frame_width, frame_height,
            LearningConfig.POINTING_LOCATION_OFFSET_PERCENTAGE,
            is_hololens)
        return image_utility.get_cropped_frame(
            frame,
            finger_pointing_region[0],
            finger_pointing_region[1],
            finger_pointing_region[2],
            finger_pointing_region[3])

    def _get_image_region_from_camera(self, camera_x, camera_y, image_width, image_height, offset_length,
                                      camera_calibration: bool):
        relative_x = camera_x
        relative_y = camera_y

        # FIXME: use camera calibration (instead of hard coded values for HL2), Add the calibration values to Camera
        if camera_calibration:
            relative_x = (relative_x + 0.18) / (0.20 + 0.18)
            relative_y = (relative_y - 0.1) / (-0.12 - 0.1)

        image_x = int(relative_x * image_width)
        image_y = int(relative_y * image_height)
        image_offset = int(offset_length * image_width / 2)
        # offset cannot be 0
        if image_offset == 0:
            return [0, 0, image_width, image_height]

        image_region = [self._get_value(image_x - image_offset, image_width),
                        self._get_value(image_y - image_offset, image_height),
                        self._get_value(image_x + image_offset, image_width),
                        self._get_value(image_y + image_offset, image_height)]

        if self._is_frame_out_of_bounds(image_region):
            return [0, 0, image_width, image_height]

        return image_region

    @staticmethod
    def _is_frame_out_of_bounds(image_region):
        if (image_region[0] in [image_region[1], image_region[2], image_region[3]] or
                image_region[1] in [image_region[2], image_region[3]] or
                image_region[2] == image_region[3]):
            return True
        return False

    @staticmethod
    def _get_value(actual, max_value):
        if actual < 0:
            return 0
        if actual > max_value:
            return max_value
        return actual
