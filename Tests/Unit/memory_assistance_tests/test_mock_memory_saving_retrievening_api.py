import pytest
from unittest import mock
import numpy as np
from pymilvus import MilvusException

# Import the main functions and utilities from the API
from Services.memory_assistance_service.memory_saving_retrieving_api import (
    enable_memory_saving,
    insert_image_memory,
    insert_text_memory,
    insert_image_text_memory,
    search_texts_by_similarity,
    search_images_by_similarity,
    search_matching_images,
)


@pytest.fixture
def mock_milvus_api(mocker):
    """Mocks all Milvus API functions used in the module."""
    # Mock the Milvus API with specific methods
    mock_milvus = mocker.patch("APIs.local_vector_db.milvus_api", autospec=True)

    # Ensure mocked connection and prevent actual database connections
    mock_milvus.connect_to_milvus.return_value = None
    mock_milvus.drop_milvus_collection.return_value = None
    mock_milvus.create_milvus_collection.return_value = None
    mock_milvus.create_milvus_index.return_value = None
    mock_milvus.insert_milvus.return_value = None
    mock_milvus.query_milvus_show_most_similar.side_effect = lambda *args, **kwargs: ["mock_result"]
    mock_milvus.query_milvus.side_effect = lambda *args, **kwargs: ["mock_result"]
    return mock_milvus


@pytest.fixture
def mock_image_utility(mocker):
    """Mocks image utility functions."""
    # Mock the image utility module
    mock_image_utility = mocker.patch("Utilities.image_utility", autospec=True)

    # Mock image-related functions with expected return values
    mock_image_utility.save_image.return_value = "mock_image_path.png"
    mock_image_utility.get_pil_image.return_value = "mock_pil_image"
    mock_image_utility.load_raw_bytes_to_opencv_frame.return_value = np.array([[1, 2], [3, 4]], dtype=np.uint8)
    mock_image_utility.load_image_to_opencv_frame.return_value = np.array([[1, 2], [3, 4]], dtype=np.uint8)
    return mock_image_utility


@pytest.fixture
def mock_local_clip(mocker):
    """Mocks the local_clip module for generating embeddings."""
    # Mock the local_clip module for generating embeddings
    mock_local_clip = mocker.patch("APIs.local_clip.local_clip", autospec=True)

    # Set expected return values for feature generation functions
    mock_local_clip.get_image_features.return_value = np.random.rand(512)
    mock_local_clip.get_text_features.return_value = np.random.rand(512)
    mock_local_clip.get_text_image_features.return_value = (np.random.rand(512), np.random.rand(512))
    return mock_local_clip


def test_enable_memory_saving(mock_milvus_api, mock_image_utility):
    """Test that memory saving setup works as expected."""
    enable_memory_saving()

    # Debugging to confirm mocks
    print("Mocked connect_to_milvus calls:", mock_milvus_api.connect_to_milvus.call_args_list)

    # Assertions for directory and collection setup
    mock_milvus_api.connect_to_milvus.assert_called_once()
    mock_milvus_api.drop_milvus_collection.assert_called_once()
    mock_milvus_api.create_milvus_collection.assert_called_once()
    mock_milvus_api.create_milvus_index.assert_called_once()


def test_insert_image_memory(mock_milvus_api, mock_image_utility, mock_local_clip):
    """Test inserting an image memory."""
    test_image_frame = np.array([[0, 1], [1, 0]], dtype=np.uint8)

    # Call the function under test
    insert_image_memory(test_image_frame)

    # Debugging to confirm mocks
    print("Mocked save_image calls:", mock_image_utility.save_image.call_args_list)

    # Verify calls
    mock_image_utility.save_image.assert_called_once()
    mock_image_utility.get_pil_image.assert_called_once_with(test_image_frame)
    mock_local_clip.get_image_features.assert_called_once_with("mock_pil_image")
    mock_milvus_api.insert_milvus.assert_called_once()


def test_insert_text_memory(mock_milvus_api, mock_local_clip):
    """Test inserting a text memory."""
    test_text = "Test memory text"

    # Call the function under test
    insert_text_memory(test_text)

    # Debugging to confirm mocks
    print("Mocked get_text_features calls:", mock_local_clip.get_text_features.call_args_list)

    # Verify calls
    mock_local_clip.get_text_features.assert_called_once_with(test_text)
    mock_milvus_api.insert_milvus.assert_called_once()


def test_insert_image_text_memory(mock_milvus_api, mock_image_utility, mock_local_clip):
    """Test inserting an image and text memory."""
    test_image_frame = np.array([[0, 1], [1, 0]], dtype=np.uint8)
    test_text = "Test memory text"

    # Call the function under test
    insert_image_text_memory(test_image_frame, test_text)

    # Debugging to confirm mocks
    print("Mocked save_image calls:", mock_image_utility.save_image.call_args_list)

    # Verify calls
    mock_image_utility.save_image.assert_called_once()
    mock_image_utility.get_pil_image.assert_called_once_with(test_image_frame)
    mock_local_clip.get_text_image_features.assert_called_once_with(test_text, "mock_pil_image")
    assert mock_milvus_api.insert_milvus.call_count == 2


def test_search_texts_by_similarity(mock_milvus_api, mock_local_clip):
    """Test searching for text similarity."""
    test_text = "Search text"
    result = search_texts_by_similarity(test_text)

    # Debugging to confirm mocks
    print("Mocked get_text_features calls:", mock_local_clip.get_text_features.call_args_list)

    # Verify calls
    mock_local_clip.get_text_features.assert_called_once_with(test_text)
    mock_milvus_api.query_milvus_show_most_similar.assert_called_once_with(
        "memory_collection", mock_local_clip.get_text_features.return_value, "embeddings", {"metric_type": "IP"}
    )
    assert result == "mock_result"


def test_search_images_by_similarity(mock_milvus_api, mock_image_utility, mock_local_clip):
    """Test searching for image similarity."""
    test_image_frame = np.array([[0, 1], [1, 0]], dtype=np.uint8)
    result = search_images_by_similarity(test_image_frame)

    # Debugging to confirm mocks
    print("Mocked get_pil_image calls:", mock_image_utility.get_pil_image.call_args_list)

    # Verify calls
    mock_image_utility.get_pil_image.assert_called_once_with(test_image_frame)
    mock_local_clip.get_image_features.assert_called_once_with("mock_pil_image")
    mock_milvus_api.query_milvus_show_most_similar.assert_called_once_with(
        "memory_collection", mock_local_clip.get_image_features.return_value, "embeddings", {"metric_type": "IP"}
    )
    assert isinstance(result, np.ndarray)


def test_search_matching_images(mock_milvus_api, mock_local_clip):
    """Test searching for similar texts or images."""
    test_text = "Search text"
    top_k = 3
    mock_milvus_api.query_milvus_show_most_similar.side_effect = lambda *args, **kwargs: ["mock_result"] * top_k

    result = search_matching_images(test_text, top_k=top_k)

    # Debugging to confirm mocks
    print("Mocked get_text_features calls:", mock_local_clip.get_text_features.call_args_list)

    # Verify calls
    mock_local_clip.get_text_features.assert_called_once_with(test_text)
    assert mock_milvus_api.query_milvus_show_most_similar.call_count == 2
    assert len(result) == top_k
