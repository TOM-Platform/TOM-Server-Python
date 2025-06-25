from unittest.mock import patch

import numpy as np
import pytest

import base_keys
from Processors.FaceDetection.detector import FaceDetector
from Processors.FaceDetection.face_detection import FaceDetection
from Utilities import image_utility
from base_component import BaseComponent


@pytest.fixture
def test_image():
    url = "https://images.unsplash.com/photo-1544005313-94ddf0286df2"
    return image_utility.get_frame(image_utility.read_image_url_bytes(url))


def test_face_detection_run(test_image):
    raw_data = {
        base_keys.CAMERA_FRAME: test_image
    }
    with patch.object(BaseComponent, 'send_to_component', return_value=None) as mock_send:
        component = FaceDetector("FaceTest")
        assert component.get_component_status() == base_keys.COMPONENT_NOT_STARTED_STATUS
        component.run(raw_data)

        assert component.get_component_status() == base_keys.COMPONENT_IS_RUNNING_STATUS
        mock_send.assert_called_once()

        # Extract the arguments passed to send_to_component
        args, kwargs = mock_send.call_args
        assert 'face_frame' in kwargs
        assert isinstance(kwargs['face_frame'], np.ndarray)
        assert kwargs['face_frame'].shape == test_image.shape


def test_face_detection_keypoint_coordinates(test_image):
    detector = FaceDetection()
    result = detector.detect(test_image)
    h, w, _ = test_image.shape

    detection = result.detections[0]

    expected_keypoints = {
        0: (2313, 2509),  # right_eye
        1: (3097, 2670),  # left_eye
        2: (2812, 3084),  # nose_tip
        3: (2655, 3483),  # mouth_center
        4: (1516, 2589),  # right_ear
        5: (3223, 2902),  # left_ear
    }

    for idx, keypoint in enumerate(detection.keypoints):
        expected_x, expected_y = expected_keypoints[idx]
        actual_x = int(keypoint.x * w)
        actual_y = int(keypoint.y * h)

        assert abs(actual_x - expected_x) <= 2, \
            f"Keypoint {idx} x mismatch: got {actual_x}, expected {expected_x}"

        assert abs(actual_y - expected_y) <= 2, \
            f"Keypoint {idx} y mismatch: got {actual_y}, expected {expected_y}"
