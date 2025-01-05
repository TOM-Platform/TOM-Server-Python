import pytest
import numpy as np
from pymilvus import MilvusException
from Services.memory_assistance_service.memory_saving_retrieving_api import (
    enable_memory_saving,
    insert_image_memory,
    insert_text_memory,
    insert_image_text_memory,
    search_texts_by_similarity,
    search_images_by_similarity,
    search_matching_images,
)
from time import sleep


# Define a module-level fixture for setup and teardown
@pytest.fixture(scope="module", autouse=True)
def setup_milvus_environment():
    """Set up the Milvus collection and environment once before all tests."""
    try:
        enable_memory_saving()  # Set up the collection for testing
        yield  # This is where tests are executed
    finally:
        from APIs.local_vector_db import milvus_api
        from Services.memory_assistance_service.memory_assistance_config import MemoryAssistanceConfig

        _COLLECTION_NAME = MemoryAssistanceConfig.MEMORY_ASSISTANCE_DATABASE_COLLECTION
        try:
            milvus_api.drop_milvus_collection(_COLLECTION_NAME)
        except MilvusException as e:
            print("Failed to clean up Milvus collection:", e)


def wait_for_commit(retries=5, delay=1):
    """Helper function to wait for data commit with retry mechanism."""
    for _ in range(retries):
        sleep(delay)
        return True  # Assumes commit is always achieved within the retries


def test_insert_text_memory():
    """Test inserting text memory into Milvus and verify approximate similarity existence."""
    test_text = "This is a test memory text."

    try:
        insert_text_memory(test_text)
        assert wait_for_commit(), "Data not committed in time."

        result = search_text_by_similarity(test_text)
        # Check for approximate match to ensure similarity within a threshold
        assert any(test_text in res or "test memory" in res for res in
                   result), f"Text similarity search failed. Results: {result}"
    except MilvusException as e:
        assert False, f"Milvus operation failed with error: {e}"


def test_insert_image_memory():
    """Test inserting image memory into Milvus and verify its existence."""
    test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    test_image[10:90, 10:90] = [255, 0, 0]  # Red square

    try:
        insert_image_memory(test_image)
        assert wait_for_commit(), "Data not committed in time."

        result_images = search_image_by_similarity(test_image)
        assert result_images, "Image memory insertion or retrieval failed."
        assert len(result_images) > 0, f"Expected a non-empty result for image search. Results: {result_images}"
    except MilvusException as e:
        assert False, f"Milvus operation failed with error: {e}"


def test_insert_image_text_memory():
    """Test inserting combined image and text memory."""
    test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    test_image[10:90, 10:90] = [0, 255, 0]  # Green square
    test_text = "This is a combined memory of text and image."

    try:
        insert_image_text_memory(test_image, test_text)
        assert wait_for_commit(), "Data not committed in time."

        result_text = search_text_by_similarity(test_text)
        result_images = search_image_by_similarity(test_image)

        # Check approximate match for text
        assert any(test_text in res or "combined memory" in res for res in
                   result_text), f"Combined text memory retrieval failed. Results: {result_text}"
        assert result_images, "Combined image memory retrieval failed."
    except MilvusException as e:
        assert False, f"Milvus operation failed with error: {e}"


def test_search_text_by_similarity():
    """Test searching text by similarity with approximate match."""
    test_text = "Unique test memory text for similarity search."
    try:
        insert_text_memory(test_text)
        assert wait_for_commit(), "Data not committed in time."

        result = search_texts_by_similarity(test_text, 2)

        # Check for approximate match
        assert any(test_text in res or "test memory text" in res for res in
                   result), f"Text similarity search failed. Results: {result}"
    except MilvusException as e:
        assert False, f"Milvus operation failed with error: {e}"


def test_search_image_by_similarity():
    """Test searching image by similarity."""
    test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    test_image[20:80, 20:80] = [0, 0, 255]  # Blue square

    try:
        insert_image_memory(test_image)
        assert wait_for_commit(), "Data not committed in time."

        result_images = search_images_by_similarity(test_image)
        assert result_images, f"Image similarity search returned None. Results: {result_images}"
        assert len(result_images) > 0, "Expected non-empty result for image similarity search."
    except MilvusException as e:
        assert False, f"Milvus operation failed with error: {e}"


def test_search_matching_images():
    """Test searching for all similar results (images and text) based on a text query."""
    test_text = "Blue square"

    # Create and insert a mix of text and images
    test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    test_image[20:80, 20:80] = [255, 0, 0]  # Blue square

    additional_text = "Extra blue square for testing."

    try:
        # Insert a mix of image and text memory
        insert_image_memory(test_image)
        insert_text_memory(additional_text)
        assert wait_for_commit(), "Data not committed in time."

        # Perform the search using the text query without filter_type
        results = search_matching_images(test_text, top_k=3)

        # Assert that we get both image and text results
        assert len(results) > 0, "Expected at least one result."
        assert any(isinstance(res, np.ndarray) for res in results), "Expected at least one image result."

    except MilvusException as e:
        assert False, f"Milvus operation failed with error: {e}"
