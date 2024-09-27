import pytest

import base64
import numpy as np
from PIL import Image
import cv2
import requests
from io import BytesIO
from unittest.mock import patch, mock_open
from Utilities.image_utility import (
    get_similarity_images,
    get_pixel_diff,
    get_cropped_frame,
    read_image_file_bytes,
    read_image_url_bytes,
    get_png_image_bytes,
    save_image,
    save_image_bytes,
    get_base64_image
)


@pytest.fixture
def sample_image_red_100() -> Image:
    return Image.new('RGB', (100, 100), color=(255, 0, 0))


@pytest.fixture
def sample_image_red_200() -> Image:
    return Image.new('RGB', (200, 200), color=(255, 0, 0))


@pytest.fixture
def sample_image_blue_100() -> Image:
    return Image.new('RGB', (100, 100), color=(0, 0, 255))


@pytest.fixture
def sample_image_blue_200() -> Image:
    return Image.new('RGB', (200, 200), color=(0, 0, 255))


@pytest.fixture
def sample_opencv_frame() -> np.ndarray:
    return np.zeros((100, 100, 3), dtype=np.uint8)


def test_get_similarity_images(sample_image_red_100: Image, sample_image_blue_100: Image, sample_image_red_200: Image,
                               sample_image_blue_200: Image):
    # For the same image (same colour and size), similarity should be 1
    similarity: float = get_similarity_images(sample_image_red_100, sample_image_red_100, 0)
    assert similarity == 1

    # For different images (same colour but different size), similarity should be 0
    similarity: float = get_similarity_images(sample_image_red_100, sample_image_red_200, 0)
    assert similarity == 0

    # For different images (different colour but same size), similarity should be 0
    similarity: float = get_similarity_images(sample_image_red_100, sample_image_blue_100, 0)
    assert similarity == 0

    # For different images (different colour and different size), similarity should be 0
    similarity: float = get_similarity_images(sample_image_red_100, sample_image_blue_200, 0)
    assert similarity == 0


def test_get_pixel_diff():
    pixel1: tuple = (255, 0, 0)
    pixel2: tuple = (0, 0, 255)
    euclid_dist: float = np.sqrt(np.sum((np.array(pixel1) - np.array(pixel2)) ** 2))
    assert get_pixel_diff(pixel1, pixel2) == euclid_dist


def test_get_cropped_frame(sample_opencv_frame: np.ndarray):
    # Get a valid 10 x 10 frame from the sample frame
    cropped_frame: np.ndarray = get_cropped_frame(sample_opencv_frame, 10, 10, 20, 20)
    assert cropped_frame.shape == (10, 10, 3)

    # Get an invalid frame from the sample frame (should be 0 x 0)
    cropped_frame: np.ndarray = get_cropped_frame(sample_opencv_frame, 300, 300, 200, 200)
    assert cropped_frame.shape == (0, 0, 3)


# Create a mock file object to read from
@patch('builtins.open', new_callable=mock_open, read_data=b'image data')
def test_read_image_file_bytes(mock_file: mock_open):
    result: bytes = read_image_file_bytes('test.jpg')

    # Check if the file was opened and read correctly
    assert result == b'image data'
    mock_file.assert_called_once_with('test.jpg', 'rb')


@patch('requests.get')
def test_read_image_url_bytes(mock_get: requests.get):
    # Create a mock response object to read from
    mock_response = requests.Response()
    mock_response.status_code = 200

    mock_response._content = b'image data'
    mock_get.return_value = mock_response
    mock_url: str = 'http://example.com/image.jpg'

    result: bytes = read_image_url_bytes('http://example.com/image.jpg')
    assert result == b'image data'
    mock_get.assert_called_once_with('http://example.com/image.jpg')


def test_get_png_image_bytes(sample_opencv_frame: np.ndarray):
    result: bytes = get_png_image_bytes(sample_opencv_frame)

    # Check if the result is bytes of a PNG image
    assert isinstance(result, bytes)
    assert result.startswith(b'\x89PNG')


# Create a mock image file object to write to
@patch('cv2.imwrite')
def test_save_image(mock_imwrite: cv2.imwrite, sample_opencv_frame: np.ndarray):
    # Save the sample frame as a PNG image
    save_image('test.png', sample_opencv_frame)

    # Check if the image was saved correctly
    mock_imwrite.assert_called_once_with('test.png', sample_opencv_frame)


# Create a mock file object to write to
@patch('builtins.open', new_callable=mock_open)
def test_save_image_bytes(mock_file: mock_open):
    # Save some image data as a PNG image
    save_image_bytes('test.png', b'image data')

    # Check if the image data was saved correctly
    mock_file.assert_called_once_with('test.png', 'wb')
    mock_file().write.assert_called_once_with(b'image data')


def test_get_base64_image(sample_image_red_100: Image):
    mock_image: Image = sample_image_red_100

    # Convert image to bytes
    img_byte_arr: BytesIO = BytesIO()
    mock_image.save(img_byte_arr, format='PNG')
    img_byte_arr: bytes = img_byte_arr.getvalue()

    result: str = get_base64_image(img_byte_arr)

    # Check if the result is a base64 encoded string
    assert isinstance(result, str)

    # Decode the base64 string to an image and check if it is the same as the original image
    decoded_image_data = base64.b64decode(result)
    img: Image = Image.open(BytesIO(decoded_image_data))
    assert img.size == (100, 100)
    assert img.mode == 'RGB'
    assert img.getpixel((0, 0)) == (255, 0, 0)  # Red color
