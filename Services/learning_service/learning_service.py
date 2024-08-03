'''
This file represents the class that handles the learning service.
'''
import statistics

import base_keys
from APIs.langchain_llm.langchain_openai import OpenAIClient
from Processors.Yolov8.video_detection import VideoDetection as YoloDetector
from base_component import BaseComponent
from DataFormat import datatypes_helper
from Utilities import image_utility, logging_utility, time_utility

from . import learning_display, learning_keys
from .learning_data_handler import build_highlight_point_data, build_learning_data
from .learning_service_config import LearningConfig

_logger = logging_utility.setup_logger(__name__)


class LearningService(BaseComponent):
    '''
    This class is responsible for handling the learning service that
    extends from BaseComponent
    '''

    def __init__(self, name):
        super().__init__(name)
        self.text_generator = OpenAIClient()
        self.image_detector = YoloDetector
        self.learning_map = {}
        self.text_detection_sent_time = 0
        self.learning_data_sent_time = 0
        self.learning_data_has_sent = False
        self.learning_data_display_duration = LearningConfig.MIN_LEARNING_CONTENT_DISPLAY_DURATION_MILLIS
        self.finger_pose_buffer = []
        self.last_point = None

    def run(self, raw_data: dict) -> None:
        '''
        This function is responsible for running the learning service
        Parameters:
        ________
        raw_data: dict
        '''
        super().set_component_status(base_keys.COMPONENT_IS_RUNNING_STATUS)
        origin = raw_data[base_keys.ORIGIN_KEY]
        if origin == base_keys.YOLOV8_PROCESSOR:
            # set the camera data frame
            self._handle_camera_data(raw_data)
        if origin == base_keys.WEBSOCKET_WIDGET:
            datatype = raw_data[base_keys.WEBSOCKET_DATATYPE]
            data = raw_data[base_keys.WEBSOCKET_MESSAGE]
            # FIXME: remove this conversion once all components are using
            # protobuf and use object values?
            data = datatypes_helper.convert_json_to_protobuf(datatype, data)
            _logger.debug("Learning Service: {datatype}", datatype=datatype)
            self._handle_websocket_data(datatype, data)

    def _send_websocket_learning_data(
            self,
            object_of_interest: str = "",
            text_content: str = "",
            speech_content: str = ""
    ) -> None:
        websocket_learning_data = build_learning_data(
            object_of_interest,
            text_content,
            speech_content
        )
        super().send_to_component(websocket_message=websocket_learning_data)

    def _send_websocket_highlight_point_data(self, x, y, z, details=""):
        websocket_highlight_point_data = build_highlight_point_data(x, y, z, details)
        super().send_to_component(websocket_message=websocket_highlight_point_data)

    def _handle_camera_data(self, raw_data):
        super().set_memory_data(base_keys.CAMERA_FRAME, raw_data[base_keys.CAMERA_FRAME])
        super().set_memory_data(base_keys.CAMERA_FRAME_WIDTH, raw_data[base_keys.CAMERA_FRAME_WIDTH])
        super().set_memory_data(base_keys.CAMERA_FRAME_HEIGHT, raw_data[base_keys.CAMERA_FRAME_HEIGHT])
        super().set_memory_data(base_keys.YOLOV8_LAST_DETECTION, raw_data[base_keys.YOLOV8_LAST_DETECTION])
        super().set_memory_data(base_keys.YOLOV8_CLASS_LABELS, raw_data[base_keys.YOLOV8_CLASS_LABELS])

    def _handle_websocket_data(
            self,
            socket_data_type,
            decoded_data
    ) -> None:
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

    def get_learning_content(
            self,
            question: str
    ) -> str:
        '''
        This function generates the learning content based on the
        object of interest, text content and speech content
        Parameters:
        ________
        question: str
            The user question
        '''
        prompt: str = f"{question}. Provide only the answer in one sentence."
        _logger.debug("Prompt: {prompt}", prompt=prompt)
        learning_content = ""
        try:
            # get cropped frame directly from the pointer data
            frame_width = super().get_memory_data(base_keys.CAMERA_FRAME_WIDTH)
            frame_height = super().get_memory_data(base_keys.CAMERA_FRAME_HEIGHT)
            frame = super().get_memory_data(base_keys.CAMERA_FRAME)
            if self.last_point is not None:
                frame = self._get_cropped_from_camera(self.last_point, frame, frame_width, frame_height)
            if frame is None:
                learning_content = self.text_generator.generate(prompt)
            else:
                # add prompt to ignore any red line or bounding boxes
                prompt = f"Please ignore all red lines, bounding boxes, labels and numbers in the image. {prompt}"
                # always take in context of frame
                image_png_bytes = image_utility.get_png_image_bytes(frame)
                learning_content = self.text_generator.generate(prompt, image_png_bytes)
        except Exception:
            _logger.exception("Error in text generation")
        return learning_content

    def _handle_learning_request(self):
        _logger.debug("Received learning request")
        # FIXME: ideally send data based on the request
        self._clear_learning_data()

    def _handle_finger_pose(self, finger_pose_data):
        # see whether the pose if pointing to an object for a certain duration
        # based on history
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
            if self.same_pointing_location(
                    prev_avg_camera_x,
                    prev_avg_camera_y,
                    finger_pose_data,
                    LearningConfig.POINTING_LOCATION_OFFSET_PERCENTAGE
            ):
                self._handle_point_select(finger_pose_data)

        # temporary store finger pose data
        self.finger_pose_buffer.append(finger_pose_data)

    def _handle_gaze_point(self, gaze_point_data):
        self._handle_point_select(gaze_point_data)

    # gaze interaction
    def _handle_point_select(self, point_data):
        # notify the selection
        self._send_websocket_highlight_point_data(
            point_data.world_x,
            point_data.world_y,
            point_data.world_z)
        # update the selection
        self.last_point = point_data
        # send the learning data
        self._send_learning_data(
            "What am I looking at currently? If there is any text, please read it.",
            is_gaze_interaction=True
        )

    # voice interaction
    def _handle_speech_data(self, speech_data):
        voice = speech_data.voice
        _logger.info("Received speech data: {voice}", voice=voice)
        if voice is not None and voice != "":
            self._send_learning_data(voice)

    def _send_learning_data(self,
                            question: str,
                            is_gaze_interaction: bool = False):
        self.learning_data_has_sent = True
        learning_content = self.get_learning_content(question)
        speak = ""
        if not is_gaze_interaction:
            speak = learning_content
        formatted_content = learning_display.get_formatted_learning_details(
            learning_content)
        # Do not need object of interest at all since previously
        # there was yolo_v8 dependency
        # second parameter is to show visually the text,
        # third is to allow hololens to speak
        self._send_websocket_learning_data("", formatted_content, speak)
        self.learning_data_display_duration = (learning_display.get_content_showing_millis(learning_content))
        _logger.debug("Learning display duration: {duration}",
                      duration=self.learning_data_display_duration)
        self.learning_data_sent_time = time_utility.get_current_millis()

    def _clear_learning_data(self) -> None:
        if (not self.learning_data_has_sent
                or time_utility.get_current_millis() - self.learning_data_sent_time < self.learning_data_display_duration):
            return
        self.learning_data_sent_time = time_utility.get_current_millis()
        self.learning_data_has_sent = False
        self._send_websocket_learning_data()

    def same_pointing_location(
            self,
            camera_x: float,
            camera_y: float,
            finger_pose_data,
            offset: float):
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
        # FIXME: hack
        if self.learning_data_has_sent:
            _logger.warn("Skip point checking")
            return False
        finger_x = finger_pose_data.camera_x
        finger_y = finger_pose_data.camera_y
        return abs(camera_x - finger_x) < offset and abs(camera_y - finger_y) < offset

    @staticmethod
    def _get_interest_objects_bounding_box(
            actual_bounding_box,
            image_width,
            image_height
    ):
        x1 = LearningService._get_value(int(actual_bounding_box[0] + 0.5), image_width)
        y1 = LearningService._get_value(int(actual_bounding_box[1] + 0.5), image_height)
        x2 = LearningService._get_value(int(actual_bounding_box[2] + 0.5), image_width)
        y2 = LearningService._get_value(int(actual_bounding_box[3] + 0.5), image_height)
        return [x1, y1, x2, y2]

    def _get_cropped_from_camera(self, point_data, frame, frame_width, frame_height):
        is_hololens = True if (frame_width == 1280 and frame_height == 720) else False
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

    @staticmethod
    def _get_unique_objects(detections, class_labels):
        confidence_threshold = LearningConfig.OBJECT_DETECTION_CONFIDENCE_THRESHOLD
        class_ids = []
        confidences = []
        for detection in detections:
            _, _, confidence, class_id, _ = detection
            if confidence > confidence_threshold:
                class_ids.append(class_id)
                confidences.append(confidence)
        if len(class_ids) == 0:
            return []
        # TODO: sort by confidence
        unique_objects = [class_labels[class_id] for class_id in set(class_ids)]
        return unique_objects

    def _get_image_region_from_camera(self, camera_x, camera_y, image_width, image_height, offset_length,
                                      camera_calibration: bool):
        relative_x = camera_x
        relative_y = camera_y

        # FIXME: use camera calibration (instead of hard coded values
        # for HL2), Add the calibration values to Camera
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

    def _is_frame_out_of_bounds(self, image_region):
        if image_region[0] == image_region[1] or image_region[0] == image_region[2] \
                or image_region[0] == image_region[3] or image_region[1] == image_region[2] \
                or image_region[1] == image_region[3] or image_region[2] == image_region[3]:
            return True
        return False

    @staticmethod
    def _get_value(actual, max_value):
        if actual < 0:
            return 0
        if actual > max_value:
            return max_value
        return actual
