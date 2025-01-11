# Credit to this tutorial by Stephen Collins for information on setting up milvus and text embedding
# https://dev.to/stephenc222/how-to-use-milvus-to-store-and-query-vector-embeddings-5hhl
'''
This is the utility class for the vector store
'''
from typing import List, Union

import numpy as np
from pymilvus import FieldSchema, CollectionSchema, DataType, Collection
from pymilvus import connections, utility
from torch import FloatTensor

from Utilities import logging_utility, time_utility

_HOST = "localhost"
_PORT = "19530"
_logger = logging_utility.setup_logger(__name__)


# FIXME: add test cases for these functions

def connect_to_milvus():
    '''
    Connect to Milvus

    throws: Exception
    '''
    try:
        connections.connect("default", host=_HOST, port=_PORT)
        _logger.debug('Connected to Milvus {host}:{port}', host=_HOST, port=_PORT)
    except Exception as e:
        _logger.exception('Failed to connect to Milvus')
        raise e


def create_milvus_collection(name: str, embeddings_len: int, labels_len: int) -> Collection:
    '''
    Create a collection in Milvus
    '''
    fields = [
        FieldSchema(name="pk", dtype=DataType.VARCHAR, is_primary=True, auto_id=True, max_length=100),
        FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=embeddings_len),
        FieldSchema(name="labels", dtype=DataType.VARCHAR, max_length=labels_len),
        FieldSchema(name="timestamp", dtype=DataType.INT64)
    ]
    description = name + "embeddings"
    collection = Collection(name, CollectionSchema(fields, description), consistency_level="Strong")
    _logger.debug('Collection {name}, embeddings_len={embeddings_len}, labels_len={labels_len} with created.',
                  name=name, embeddings_len=embeddings_len, labels_len=labels_len)
    return collection


def check_collection_exists(name: str) -> bool:
    '''
    Check if a collection exists in Milvus
    '''
    return utility.has_collection(name)


def drop_milvus_collection(name: str) -> bool:
    '''
    Drop a collection in Milvus
    '''

    if not check_collection_exists(name):
        _logger.debug('Collection {name} does not exist.', name=name)
        return False

    collection = Collection(name)
    collection.drop()
    _logger.debug('Collection {name} dropped.', name=name)
    return True


def generate_entities(embeddings: FloatTensor, labels: List[str], times=None) -> List:
    '''
    Generate entities for insertion into Milvus
    '''
    if times is None:
        times = [time_utility.get_current_millis() for _ in range(len(embeddings))]

    entities = [
        embeddings,
        labels,
        times
    ]
    return entities


def insert_milvus(entities, name: str):
    '''
    Insert entities into Milvus
    '''
    collection = Collection(name)
    result = collection.insert(entities)
    _logger.debug('Inserted {size} entities.', size=len(entities[0]))
    return result


def create_milvus_index(collection_name, field_name, index_type="IVF_FLAT", metric_type="L2", params=None):
    '''
    Create an index in Milvus
    '''
    if params is None:
        params = {"nlist": 128}

    collection = Collection(collection_name)
    index = {"index_type": index_type, "metric_type": metric_type, "params": params}
    collection.create_index(field_name, index)
    _logger.debug('Index created for {collection_name}.', collection_name=collection_name)


def query_milvus(
        collection_data: Union[str, Collection],
        search_vectors: Union[np.ndarray, FloatTensor],
        search_field: str,
        search_params: dict,
        top_k: int = 3
) -> List:
    """
    Query Milvus for the most similar embeddings.

    :param collection_data: The name of the collection or the Collection object itself.
    :param search_vectors: The vector(s) to search for (tensor or numpy array).
    :param search_field: The field in the collection to search.
    :param search_params: Parameters for the search (such as metric type).
    :param top_k: Number of top similar results to return.
    :return: List of search results, each containing either image paths or text labels.
    """
    # Load the collection if provided as a string
    if isinstance(collection_data, str):
        collection_data = Collection(collection_data)
    collection_data.load()

    # Ensure search_vectors is a list of lists (convert from tensor if needed)
    if hasattr(search_vectors, "detach"):  # for PyTorch tensors
        embeddings = search_vectors.detach().cpu().numpy().tolist()
    elif isinstance(search_vectors, np.ndarray):
        embeddings = search_vectors.tolist()
    else:
        raise TypeError("search_vectors must be either a PyTorch tensor or a numpy array")

    # Perform the search with the specified top_k
    result = collection_data.search(
        data=embeddings,
        anns_field=search_field,
        param=search_params,
        limit=top_k,
        output_fields=["labels"]
    )

    return result  # Return the full list of results


def query_milvus_show_most_similar(
        collection_data: Union[str, Collection],
        search_vectors: FloatTensor,
        search_field: str,
        search_params: dict,
        top_k: int = 1,
        filter_type: str = None  # 'image', 'text', or None for all
) -> List[str]:
    """
    Shows the most similar items (labels or image paths) from Milvus.

    :param collection_data: The name of the collection or the Collection object itself.
    :param search_vectors: The vector(s) to search for.
    :param search_field: The field in the collection to search.
    :param search_params: Parameters for the search (such as metric type).
    :param top_k: Number of top similar results to return.
    :param filter_type: Type of data to return ('image' or 'text'). If None, return all results.
    :return: A list of top_k similar labels or image paths.
    """
    # Perform the search using the underlying `query_milvus` function
    search_results = query_milvus(
        collection_data,
        search_vectors,
        search_field,
        search_params,
        top_k=top_k * 2  # consider text + image type, and will be filtered later by type to correct 'top_k' count
    )

    # Check for common image extensions if filtering for images
    image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff'}
    filtered_results = []

    all_results = search_results[0]  # Assuming search_results[0] contains Hits
    _logger.debug('Similar results length {len}.', len=len(all_results))

    # Loop through each hit and access the labels correctly
    for hit in all_results:
        label = hit.get("labels")  # Use .get() for dictionary-like access
        _logger.debug('Similar results: {label}.', label=label)
        if filter_type == 'image' and any(label.lower().endswith(ext) for ext in image_extensions):
            filtered_results.append(label)
        elif filter_type == 'text' and not any(label.lower().endswith(ext) for ext in image_extensions):
            filtered_results.append(label)
        elif filter_type is None:
            # No filtering; add all results
            filtered_results.append(label)

    return filtered_results[:top_k]


if __name__ == "__main__":
    connect_to_milvus()
    create_milvus_collection("ImageBind", 1024, 5000)
    drop_milvus_collection("ImageBind")
