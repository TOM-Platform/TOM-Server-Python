import pytest
from pymilvus import connections, Collection
import time
import numpy as np

# Import the functions to be tested
from APIs.local_vector_db.milvus_api import (
    connect_to_milvus,
    create_milvus_collection,
    check_collection_exists,
    drop_milvus_collection,
    generate_entities,
    insert_milvus,
    create_milvus_index,
    query_milvus,
    query_milvus_show_most_similar,
)


@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    """Setup and teardown for the entire module."""
    connect_to_milvus()
    yield
    # Teardown: Drop test collections if they exist
    if check_collection_exists("test_collection"):
        drop_milvus_collection("test_collection")
    connections.disconnect("default")


def test_connect_to_milvus():
    """Test connecting to Milvus."""
    assert connections.has_connection("default")


def test_create_milvus_collection():
    """Test creating a Milvus collection."""
    name = "test_collection"
    embeddings_len = 128
    labels_len = 50

    collection = create_milvus_collection(name, embeddings_len, labels_len)
    assert collection.name == name
    assert check_collection_exists(name)

    # Cleanup
    drop_milvus_collection(name)


def test_check_collection_exists():
    """Test checking if a collection exists."""
    name = "test_collection"
    embeddings_len = 128
    labels_len = 50

    create_milvus_collection(name, embeddings_len, labels_len)
    assert check_collection_exists(name)

    # Cleanup
    drop_milvus_collection(name)


def test_drop_milvus_collection_exists():
    """Test dropping an existing Milvus collection."""
    name = "test_collection"
    embeddings_len = 128
    labels_len = 50

    create_milvus_collection(name, embeddings_len, labels_len)
    assert drop_milvus_collection(name)
    assert not check_collection_exists(name)  # Ensure it no longer exists


def test_drop_milvus_collection_not_exists():
    """Test dropping a non-existent collection."""
    name = "non_existent_collection"
    result = drop_milvus_collection(name)
    assert not result  # Should return False or similar for non-existent collection


def test_generate_entities():
    """Test generating entities for insertion."""
    embeddings = [[0.1, 0.2, 0.3]]
    labels = ["label1"]
    times = [1625097600]

    result = generate_entities(embeddings, labels, times)
    assert result == [embeddings, labels, times]


def test_insert_milvus():
    """Test inserting entities into Milvus."""
    name = "test_collection"
    embeddings_len = 128
    labels_len = 50

    create_milvus_collection(name, embeddings_len, labels_len)

    # Create valid embeddings with length matching embeddings_len
    embeddings = [[0.1] * embeddings_len]
    labels = ["label1"]
    times = [int(time.time())]

    entities = generate_entities(embeddings, labels, times)
    insert_result = insert_milvus(entities, name)
    assert insert_result is not None, "Insert operation failed"  # Ensure result is not None
    assert hasattr(insert_result, 'primary_keys') and len(insert_result.primary_keys) > 0

    # Cleanup
    drop_milvus_collection(name)


def test_create_milvus_index():
    """Test creating an index on a Milvus collection."""
    name = "test_collection"
    embeddings_len = 128
    labels_len = 50

    create_milvus_collection(name, embeddings_len, labels_len)

    index_params = {"nlist": 128}
    create_milvus_index(name, "embeddings", "IVF_FLAT", "L2", index_params)

    collection = Collection(name)
    indexes = collection.indexes
    assert len(indexes) > 0
    assert indexes[0].params["metric_type"] == "L2"  # Verify metric type
    assert indexes[0].params["index_type"] == "IVF_FLAT"

    # Cleanup
    drop_milvus_collection(name)


def test_query_milvus():
    """Test querying similar embeddings in Milvus."""
    name = "test_collection"
    embeddings_len = 128
    labels_len = 50

    create_milvus_collection(name, embeddings_len, labels_len)

    # Insert some embeddings to query
    embeddings = [[0.1] * embeddings_len]
    labels = ["label1"]
    times = [int(time.time())]

    entities = generate_entities(embeddings, labels, times)
    insert_milvus(entities, name)

    # Create the index before querying
    index_params = {"nlist": 128}
    create_milvus_index(name, "embeddings", "IVF_FLAT", "L2", index_params)

    # Convert search_vectors to np.ndarray for query compatibility
    search_vectors = np.array([[0.1] * embeddings_len])
    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}

    result = query_milvus(name, search_vectors, "embeddings", search_params)
    assert len(result) > 0

    # Access the label data within the query results
    labels = [hit.get("labels") for hit in result[0]]  # Use .get to access labels in each Hit
    assert "label1" in labels  # Ensure the correct label is found

    # Cleanup
    drop_milvus_collection(name)


def test_query_milvus_show_most_similar_text_filter():
    """Test querying Milvus with a text filter to retrieve text-only results."""
    name = "test_collection"
    embeddings_len = 128
    labels_len = 50

    create_milvus_collection(name, embeddings_len, labels_len)

    # Insert text data into Milvus
    text_embeddings = [[0.2] * embeddings_len]
    labels = ["text_label"]
    times = [int(time.time())]

    entities = generate_entities(text_embeddings, labels, times)
    insert_milvus(entities, name)

    # Create an index before querying
    index_params = {"nlist": 128}
    create_milvus_index(name, "embeddings", "IVF_FLAT", "L2", index_params)

    # Query with text filter
    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
    result = query_milvus_show_most_similar(
        collection_data=name,
        search_vectors=np.array([[0.2] * embeddings_len]),
        search_field="embeddings",
        search_params=search_params,
        top_k=1,
        filter_type="text"
    )

    assert "text_label" in result, f"Expected 'text_label' in results, got {result}"

    # Cleanup
    drop_milvus_collection(name)


def test_query_milvus_show_most_similar_image_filter():
    """Test querying Milvus with an image filter to retrieve image-only results."""
    name = "test_collection"
    embeddings_len = 128
    labels_len = 50

    create_milvus_collection(name, embeddings_len, labels_len)

    # Insert image data into Milvus
    image_embeddings = [[0.3] * embeddings_len]
    labels = ["image_label.png"]  # Label ends with image extension
    times = [int(time.time())]

    entities = generate_entities(image_embeddings, labels, times)
    insert_milvus(entities, name)

    # Create an index before querying
    index_params = {"nlist": 128}
    create_milvus_index(name, "embeddings", "IVF_FLAT", "L2", index_params)

    # Query with image filter
    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
    result = query_milvus_show_most_similar(
        collection_data=name,
        search_vectors=np.array([[0.3] * embeddings_len]),
        search_field="embeddings",
        search_params=search_params,
        top_k=1,
        filter_type="image"
    )

    assert "image_label.png" in result, f"Expected 'image_label.png' in results, got {result}"

    # Cleanup
    drop_milvus_collection(name)
