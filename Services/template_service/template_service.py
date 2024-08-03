import math
import numpy
import base_keys
from DataFormat import datatypes_helper
from Processors.Yolov8.video_detection import VideoDetection as YoloDetector
from Utilities import image_utility
from Utilities import logging_utility
from base_component import BaseComponent
from .template_data_handler import build_template_data

_logger = logging_utility.setup_logger(__name__)


class TemplateService(BaseComponent):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.image_detector: YoloDetector = YoloDetector

    def run(self, raw_data: dict) -> None:
        super().set_component_status(base_keys.COMPONENT_IS_RUNNING_STATUS)

        origin = raw_data[base_keys.ORIGIN_KEY]

        if origin == base_keys.WEBSOCKET_WIDGET:
            datatype = raw_data[base_keys.WEBSOCKET_DATATYPE]
            data = raw_data[base_keys.WEBSOCKET_MESSAGE]

            data = datatypes_helper.convert_json_to_protobuf(datatype, data)
            _logger.debug("Template Service: {datatype}", datatype=datatype)

            self._handle_websocket_data(datatype, data)

        if origin == base_keys.YOLOV8_PROCESSOR:
            self._handle_camera_data(raw_data)

    def _handle_websocket_data(self, socket_data_type, decoded_data):
        if socket_data_type == datatypes_helper.get_key_by_name("REQUEST_TEMPLATE_DATA"):
            return self._handle_template_request(decoded_data)

    def _handle_template_request(self, decoded_data):
        try:
            label, image = self._get_detected_label_and_image()
            self._send_websocket_template_data(text=label, image=image, audio_path="two_beep_audio")
        except Exception as e:
            # No object is detected
            _logger.error("Error getting detected label and image: {e}", e=e)
            return

    # Build the template data in protobuf format and send it to the template scene

    def _send_websocket_template_data(self, text: str = "", image: bytes = None, audio_path: str = "") -> None:
        '''
        Sending websocket data to the template scene

        :param text: text to be displayed
        :param image: bytes of the image
        :param audio_path: the audio file name without the extension.
            The audio file should be in the "Assets/Resources/Audio" folder of the Unity Client
        :return: None
        '''
        websocket_template_data = build_template_data(text=text, image=image, audio_path=audio_path)

        super().send_to_component(websocket_message=websocket_template_data)

        _logger.info("Template Data (Text: {text}, Image, Audio: {audio_path}) sent to Template Scene",
                     text=text, image=image, audio_path=audio_path)

    # Set the camera frame, frame width, frame height, last detection and class labels in the "shared" memory
    def _handle_camera_data(self, raw_data: dict) -> None:
        super().set_memory_data(base_keys.CAMERA_FRAME, raw_data[base_keys.CAMERA_FRAME])
        super().set_memory_data(base_keys.CAMERA_FRAME_WIDTH, raw_data[base_keys.CAMERA_FRAME_WIDTH])
        super().set_memory_data(base_keys.CAMERA_FRAME_HEIGHT, raw_data[base_keys.CAMERA_FRAME_HEIGHT])
        super().set_memory_data(base_keys.YOLOV8_LAST_DETECTION, raw_data[base_keys.YOLOV8_LAST_DETECTION])
        super().set_memory_data(base_keys.YOLOV8_CLASS_LABELS, raw_data[base_keys.YOLOV8_CLASS_LABELS])

    # Get frame data from memory and get the detected label and image
    def _get_detected_label_and_image(self) -> tuple:
        frame_detections: dict = super().get_memory_data(base_keys.YOLOV8_LAST_DETECTION)
        frame: numpy.ndarray = super().get_memory_data(base_keys.CAMERA_FRAME)
        frame_width: int = super().get_memory_data(base_keys.CAMERA_FRAME_WIDTH)
        frame_height: int = super().get_memory_data(base_keys.CAMERA_FRAME_HEIGHT)
        class_labels: dict = super().get_memory_data(base_keys.YOLOV8_CLASS_LABELS)

        label, image = self._get_first_yolov8_detection(frame_detections, frame, frame_width, frame_height,
                                                        class_labels)
        return label, image

    # Get the first detected label and image from the frame detections
    def _get_first_yolov8_detection(self, frame_detections: dict, frame: numpy.ndarray, frame_width: int,
                                    frame_height: int, class_labels: dict) -> tuple:
        detections = YoloDetector.get_detection_in_region(frame_detections, [0, 0, frame_width, frame_height])

        if detections is None or len(detections.class_id) == 0:
            return None, None
        else:
            # take the first detection
            class_id: int = detections.class_id[0]
            xy_bounds: list = detections.xyxy[0]
            label: str = class_labels[class_id]

            # Crop the frame to the bounding box of the detected object and convert it to bytes before sending it to the template scene
            image_frame: numpy.ndarray = image_utility.get_cropped_frame(frame, math.floor(xy_bounds[0]),
                                                                         math.floor(xy_bounds[1]),
                                                                         math.floor(xy_bounds[2]),
                                                                         math.floor(xy_bounds[3]))
            image: bytes = image_utility.get_png_image_bytes(image_frame)

            return label, image
