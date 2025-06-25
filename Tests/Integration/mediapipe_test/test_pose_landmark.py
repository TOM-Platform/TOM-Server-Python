from unittest.mock import patch

import numpy as np
import pytest

import base_keys
from Processors.PoseLandmarkDetection.detector import PoseLandmarkDetector
from Processors.PoseLandmarkDetection.pose_landmark_detection import PoseLandmarkDetection
from Utilities import image_utility
from base_component import BaseComponent


@pytest.fixture
def test_image():
    url = "https://cdn.pixabay.com/photo/2019/03/12/20/39/girl-4051811_960_720.jpg"
    return image_utility.get_frame(image_utility.read_image_url_bytes(url))


def test_pose_landmark_detection_run(test_image):
    raw_data = {
        base_keys.CAMERA_FRAME: test_image
    }
    with patch.object(BaseComponent, 'send_to_component', return_value=None) as mock_send:
        component = PoseLandmarkDetector("PoseTest")
        assert component.get_component_status() == base_keys.COMPONENT_NOT_STARTED_STATUS
        component.run(raw_data)

        assert component.get_component_status() == base_keys.COMPONENT_IS_RUNNING_STATUS
        mock_send.assert_called_once()

        # Extract the arguments passed to send_to_component
        args, kwargs = mock_send.call_args
        assert 'pose_frame' in kwargs
        assert isinstance(kwargs['pose_frame'], np.ndarray)
        assert kwargs['pose_frame'].shape == test_image.shape


def test_pose_landmark_coordinates_deterministic(test_image):
    detector = PoseLandmarkDetection()
    result = detector.detect(test_image)
    h, w, _ = test_image.shape

    pose_landmarks = result.pose_landmarks[0]  # Person 0

    expected_coordinates = {
        0: (334, 126),  # nose
        1: (339, 107),  # left_eye_inner
        2: (346, 104),  # left_eye
        3: (353, 102),  # left_eye_outer
        4: (323, 111),  # right_eye_inner
        5: (319, 113),  # right_eye
        6: (316, 113),  # right_eye_outer
        7: (370, 103),  # left_ear
        8: (315, 116),  # right_ear
        9: (352, 137),  # mouth_left
        10: (331, 142),  # mouth_right
        11: (453, 184),  # left_shoulder
        12: (296, 200),  # right_shoulder
        13: (539, 260),  # left_elbow
        14: (240, 275),  # right_elbow
        15: (581, 325),  # left_wrist
        16: (244, 351),  # right_wrist
        17: (596, 357),  # left_pinky
        18: (240, 381),  # right_pinky
        19: (586, 358),  # left_index
        20: (254, 371),  # right_index
        21: (578, 345),  # left_thumb
        22: (259, 365),  # right_thumb
        23: (435, 389),  # left_hip
        24: (353, 398),  # right_hip
        25: (570, 304),  # left_knee
        26: (338, 252),  # right_knee
        27: (718, 434),  # left_ankle
        28: (438, 393),  # right_ankle
        29: (722, 462),  # left_heel
        30: (462, 422),  # right_heel
        31: (810, 429),  # left_foot_index
        32: (449, 419),  # right_foot_index
    }

    for idx, (expected_x, expected_y) in expected_coordinates.items():
        actual_x = int(pose_landmarks[idx].x * w)
        actual_y = int(pose_landmarks[idx].y * h)

        assert abs(actual_x - expected_x) <= 2, \
            f"Landmark {idx} x mismatch: got {actual_x}, expected {expected_x}"

        assert abs(actual_y - expected_y) <= 2, \
            f"Landmark {idx} y mismatch: got {actual_y}, expected {expected_y}"
