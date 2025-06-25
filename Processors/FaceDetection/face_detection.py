from typing import Tuple, Union
import math
import cv2
import numpy as np

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from Utilities import environment_utility, logging_utility, file_utility

_logger = logging_utility.setup_logger(__name__)

MARGIN = 10  # pixels
ROW_SIZE = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
TEXT_COLOR = (255, 0, 0)  # blue in BGR (OpenCV)

BOUNDING_BOX_COLOR = (0, 0, 255)  # red in BGR (OpenCV)
BOUNDING_BOX_THICKNESS = 3

KEYPOINT_SIZE = 2
KEYPOINT_THICKNESS = 2
KEYPOINT_COLOR = (0, 255, 0)  # green in RGB format

_MODEL_ASSET_PATH = environment_utility.get_env_string("FACE_DETECTION_MODEL")


class FaceBoundingBox:
    """
    Represents a normalized bounding box for a detected face.
    """

    def __init__(self, origin_x: float, origin_y: float, width: float, height: float):
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.width = width
        self.height = height

    def to_dict(self):
        return {
            "origin_x": self.origin_x,
            "origin_y": self.origin_y,
            "width": self.width,
            "height": self.height,
        }


class Face:
    """
    Stores the results of face detection in a picklable format.
    """

    def __init__(self, bounding_box: FaceBoundingBox, score: float, category_name: str):
        self.bounding_box = bounding_box
        self.score = score
        self.category_name = category_name

    def to_dict(self):
        return {
            "bounding_box": self.bounding_box.to_dict(),
            "score": self.score,
            "category_name": self.category_name
        }


class Faces:
    """
    Stores multiple face detections in a picklable format.
    """

    def __init__(self, detections: list[Face]):
        self.detections = detections

    @classmethod
    def from_mediapipe(cls, mp_result):
        """
        Converts a MediaPipe FaceDetectorResult to a picklable format.
        See: https://ai.google.dev/edge/mediapipe/solutions/vision/face_detector/python#handle_and_display_results

        Args:
            mp_result: MediaPipe FaceDetectorResult

        Returns:
            FaceDetections instance
        """
        face_detections = []

        for det in mp_result.detections:
            bbox = det.bounding_box
            category = det.categories[0] if det.categories else None
            face_detections.append(
                Face(
                    bounding_box=FaceBoundingBox(
                        origin_x=bbox.origin_x,
                        origin_y=bbox.origin_y,
                        width=bbox.width,
                        height=bbox.height
                    ),
                    score=category.score if category else 0.0,
                    category_name=category.category_name if category else ""
                )
            )

        return cls(face_detections)


class FaceDetection:
    """
    Use MediaPipe for face detection with OpenCV frames

    Details: https://ai.google.dev/edge/mediapipe/solutions/vision/face_detector
    """

    def __init__(self):
        model_absolute_path = file_utility.get_path_with_filename(file_utility.get_project_root(), _MODEL_ASSET_PATH)
        base_options = python.BaseOptions(model_asset_path=model_absolute_path)
        options = vision.FaceDetectorOptions(base_options=base_options,
                                             running_mode=vision.RunningMode.IMAGE,
                                             min_detection_confidence=0.6)
        self.detector = vision.FaceDetector.create_from_options(options)

    def detect(self, frame: np.ndarray):
        """
        Detect face in a frame

        Args:
            frame: OpenCV frame (BGR format)

        Returns:
            MediaPipe detection result
        """

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB for MediaPipe
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        return self.detector.detect(image)

    def close(self):
        self.detector.close()


def _normalized_to_pixel_coordinates(
        normalized_x: float, normalized_y: float, image_width: int, image_height: int) -> Union[None, Tuple[int, int]]:
    """
    Converts normalized value pair to pixel coordinates.

    Args:
        normalized_x: Normalized x coordinate (0-1)
        normalized_y: Normalized y coordinate (0-1)
        image_width: Width of the image in pixels
        image_height: Height of the image in pixels

    Returns:
        Tuple of pixel coordinates or None if values are invalid
    """

    # Checks if the float value is between 0 and 1.
    def is_valid_normalized_value(value: float) -> bool:
        return (value > 0 or math.isclose(0, value)) and (value < 1 or math.isclose(1, value))

    if not (is_valid_normalized_value(normalized_x) and
            is_valid_normalized_value(normalized_y)):
        # TODO: Draw coordinates even if it's outside of the image bounds.
        return None
    x_px = min(math.floor(normalized_x * image_width), image_width - 1)
    y_px = min(math.floor(normalized_y * image_height), image_height - 1)
    return x_px, y_px


def visualize(
        image,
        detection_result
) -> np.ndarray:
    """
    Draws bounding boxes and keypoints on the input image and return it.

    Args:
      image: The input BGR image (OpenCV format).
      detection_result: The list of all "Detection" entities to be visualize.

    Returns:
      Image with bounding boxes.
    """
    annotated_image = image.copy()
    height, width, _ = image.shape

    for detection in detection_result.detections:
        # Draw bounding_box
        bbox = detection.bounding_box
        sx, sy = int(bbox.origin_x), int(bbox.origin_y)
        ex, ey = int(bbox.origin_x + bbox.width), int(bbox.origin_y + bbox.height)
        cv2.rectangle(annotated_image, (sx, sy), (ex, ey), BOUNDING_BOX_COLOR, BOUNDING_BOX_THICKNESS)

        # Draw keypoints
        for keypoint in detection.keypoints:
            keypoint_px = _normalized_to_pixel_coordinates(keypoint.x, keypoint.y, width, height)

            if keypoint_px is not None:
                # Green circle in BGR
                cv2.circle(annotated_image, keypoint_px, KEYPOINT_SIZE, KEYPOINT_COLOR, KEYPOINT_THICKNESS)
            else:
                _logger.warning("keypoint_px not found : {keypoint_px}", keypoint_px=keypoint_px)

        # Draw label and score
        category = detection.categories[0]
        category_name = category.category_name
        category_name = '' if category_name is None else category_name
        probability = round(category.score, 2)
        result_text = category_name + ' (' + str(probability) + ')'
        text_location = (MARGIN + bbox.origin_x, MARGIN + ROW_SIZE + bbox.origin_y)
        cv2.putText(annotated_image, result_text, text_location, cv2.FONT_HERSHEY_PLAIN, FONT_SIZE, TEXT_COLOR,
                    FONT_THICKNESS)

    return annotated_image
