# coding=utf-8

import pytest
import cv2
from unittest.mock import MagicMock
from APIs.cloud_vision.VisionClient import VisionClient as TextDetector


@pytest.fixture
def mock_vision_client():
    """Fixture to mock VisionClient."""
    client = TextDetector()
    client.client = MagicMock()  # Mock the client attribute
    return client


def test_detect_text_image_uri():
    text_detector = TextDetector()
    res, _, _ = text_detector.detect_text_image_uri("gs://cloud-samples-data/vision/ocr/sign.jpg")

    assert ",".join(res) == 'WAITING?\nPLEASE\nTURN OFF\nYOUR\nENGINE,WAITING,?,PLEASE,TURN,OFF,YOUR,ENGINE'


def test_detect_text_frame():
    cap = cv2.VideoCapture(
        0)  # 0 is the default camera. Replace with the file path for an image file.
    ret, frame = cap.read()

    text_detector = TextDetector()
    res, _, _ = text_detector.detect_text_frame(frame)

    assert res == []


def test_detect_objects_landmarks(mock_vision_client):
    # Define mock response
    mock_response = MagicMock()

    # Create mock objects for localized object annotations
    object1 = MagicMock(name='FakeObject')
    object1.name = 'object1'
    object1.score = 0.95
    object1.bounding_poly = MagicMock(vertices=[{'x': 10, 'y': 20}, {'x': 30, 'y': 40}])

    object2 = MagicMock(name='FakeObject')
    object2.name = 'object2'
    object2.score = 0.85
    object2.bounding_poly = MagicMock(vertices=[{'x': 50, 'y': 60}, {'x': 70, 'y': 80}])

    mock_response.localized_object_annotations = [object1, object2]

    # Create mock objects for landmark annotations
    landmark1 = MagicMock(name='FakeLandmark')
    landmark1.description = 'landmark1'
    landmark1.score = 0.90
    landmark1.bounding_poly = MagicMock(vertices=[{'x': 15, 'y': 25}, {'x': 35, 'y': 45}])

    landmark2 = MagicMock(name='FakeLandmark')
    landmark2.description = 'landmark2'
    landmark2.score = 0.80
    landmark2.bounding_poly = MagicMock(vertices=[{'x': 55, 'y': 65}, {'x': 75, 'y': 85}])

    mock_response.landmark_annotations = [landmark1, landmark2]

    # Mock the annotate_image method
    mock_vision_client.client.annotate_image.return_value = mock_response

    image_bytes = b'fake_image_bytes'  # Example placeholder
    descriptions, scores, bounding_boxes, types = mock_vision_client.detect_objects_landmarks(image_bytes)

    # Assertions
    assert descriptions == ['object1', 'object2', 'landmark1', 'landmark2']
    assert scores == [0.95, 0.85, 0.90, 0.80]
    assert bounding_boxes == [
        [{'x': 10, 'y': 20}, {'x': 30, 'y': 40}],
        [{'x': 50, 'y': 60}, {'x': 70, 'y': 80}],
        [{'x': 15, 'y': 25}, {'x': 35, 'y': 45}],
        [{'x': 55, 'y': 65}, {'x': 75, 'y': 85}]
    ]
    assert types == ['object', 'object', 'landmark', 'landmark']
