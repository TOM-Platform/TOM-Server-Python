import pytest
from Utilities.camera_utility import get_image_region, clamp_value, is_frame_invalid


def test_get_image_region_without_calibration():
    """
    Test the get_image_region method without camera calibration.
    """
    camera_x, camera_y = 0.5, 0.5
    image_width, image_height = 1920, 1080
    offset_percentage = 0.2
    calibrate_camera = False

    region = get_image_region(camera_x, camera_y, image_width, image_height, offset_percentage, calibrate_camera)

    expected_offset_x = int(offset_percentage * image_width / 2)
    expected_offset_y = int(offset_percentage * image_height / 2)
    expected_x = int(camera_x * image_width)
    expected_y = int(camera_y * image_height)

    expected_region = [
        max(0, expected_x - expected_offset_x),
        max(0, expected_y - expected_offset_y),
        min(image_width - 1, expected_x + expected_offset_x),
        min(image_height - 1, expected_y + expected_offset_y)
    ]

    assert region == expected_region


def test_get_image_region_with_calibration():
    """
    Test the get_image_region method with camera calibration.
    """
    camera_x, camera_y = 0.1, -0.1  # Raw input values
    image_width, image_height = 1920, 1080
    offset_percentage = 0.1
    calibrate_camera = True

    region = get_image_region(camera_x, camera_y, image_width, image_height, offset_percentage, calibrate_camera)

    # Manually computing expected values with calibration
    relative_x = (camera_x + 0.18) / (0.20 + 0.18)
    relative_y = (camera_y - 0.1) / (-0.12 - 0.1)
    expected_x = int(relative_x * image_width)
    expected_y = int(relative_y * image_height)
    expected_offset_x = max(1, int(offset_percentage * image_width / 2))
    expected_offset_y = max(1, int(offset_percentage * image_height / 2))

    expected_region = [
        max(0, expected_x - expected_offset_x),
        max(0, expected_y - expected_offset_y),
        min(image_width - 1, expected_x + expected_offset_x),
        min(image_height - 1, expected_y + expected_offset_y)
    ]

    assert region == expected_region


def test_get_image_region_full_offset():
    """
    Test case when offset_percentage is 0, expecting the full image.
    """
    camera_x, camera_y = 0.5, 0.5
    image_width, image_height = 1920, 1080
    offset_percentage = 100  # Edge case
    calibrate_camera = False

    region = get_image_region(camera_x, camera_y, image_width, image_height, offset_percentage, calibrate_camera)
    assert region == [0, 0, image_width-1, image_height-1]


def test_clamp_value():
    """
    Test the _clamp_value method to ensure it properly constrains values.
    """
    assert clamp_value(-10, 100) == 0
    assert clamp_value(50, 100) == 50
    assert clamp_value(120, 100) == 100 # max_value


def test_is_frame_invalid():
    """
    Test the _is_frame_invalid method to detect invalid frames.
    """
    assert is_frame_invalid(100, 200, 100, 250)  # x_min == x_max (invalid)
    assert is_frame_invalid(150, 300, 180, 300)  # y_min == y_max (invalid)
    assert not is_frame_invalid(100, 200, 200, 300)  # Valid frame