import numpy as np
from pymilvus import MilvusException

from APIs.local_clip import local_clip
from APIs.local_vector_db import milvus_api
from Utilities import image_utility, file_utility, time_utility, format_utility, logging_utility
from .memory_assistance_config import MemoryAssistanceConfig

_CLIP_EMBEDDINGS_LENGTH = 512  # Fixed length of CLIP embeddings
_LABELS_LENGTH = 5000  # Each memory can contain a label of up to 5000 characters.
# For image memories, this is the name of the file, and for text memories, this is the text itself.

_COLLECTION_NAME = MemoryAssistanceConfig.MEMORY_ASSISTANCE_DATABASE_COLLECTION

_IMAGES_DIRECTORY = MemoryAssistanceConfig.MEMORY_ASSISTANCE_IMAGES_DIRECTORY

_logger = logging_utility.setup_logger(__name__)


def _save_image(image_frame):
    '''
    Save the image to the `images` directory.
    :param image_frame: The (OpenCV) image frame to save.
    :return: The image path.
    '''
    image_path = f"{_IMAGES_DIRECTORY}/{time_utility.get_current_millis()}.png"
    image_utility.save_image(image_path, image_frame)
    return image_path


def enable_memory_saving():
    '''
    Enable memory saving.

    throws: MilvusException
    '''
    # create the file directory
    file_utility.create_directory(_IMAGES_DIRECTORY)

    # create the collection
    milvus_api.connect_to_milvus()
    # FIXME: disable this
    milvus_api.drop_milvus_collection(_COLLECTION_NAME)

    # create collection if it does not exist
    if not milvus_api.check_collection_exists(_COLLECTION_NAME):
        milvus_api.create_milvus_collection(_COLLECTION_NAME, _CLIP_EMBEDDINGS_LENGTH, _LABELS_LENGTH)

    # index needs to be created in order to perform search operations
    milvus_api.create_milvus_index(_COLLECTION_NAME, "embeddings", metric_type="IP")


def insert_image_memory(image_frame):
    '''
    Insert the image memories into the given collection.
    :param image_frame: The image to insert.

    throws: MilvusException
    '''
    # save the image
    image_path = _save_image(image_frame)
    # get the image features
    pil_image = image_utility.get_pil_image(image_frame)
    image_features = local_clip.get_image_features(pil_image)

    # generate entities and save them
    image_entities = milvus_api.generate_entities(image_features, [image_path])
    insert_result = milvus_api.insert_milvus(image_entities, _COLLECTION_NAME)
    if insert_result is None:
        _logger.warn("Image memory insertion failed")
        raise MilvusException(message="Image memory insertion failed")


def insert_text_memory(text: str):
    '''
    Insert the text memories into the given collection.
    :param text: The text to insert.

    throws: MilvusException
    '''
    # get the text features
    text_features = local_clip.get_text_features(text)

    # generate entities and save them
    text_entities = milvus_api.generate_entities(text_features, [text])
    insert_result = milvus_api.insert_milvus(text_entities, _COLLECTION_NAME)
    if insert_result is None:
        _logger.warn("Text memory insertion failed")
        raise MilvusException(message="Text memory insertion failed")


def insert_image_text_memory(image_frame, text: str):
    '''
    Insert the image + text memories into the given collection.
    :param image_frame: The image to insert.
    :param text: The text to insert.

    throws: MilvusException
    '''
    # save the image
    image_path = _save_image(image_frame)
    # get the image features
    pil_image = image_utility.get_pil_image(image_frame)
    text_features, image_features = local_clip.get_text_image_features(text, pil_image)

    # generate entities and save them
    image_entities = milvus_api.generate_entities(image_features, [image_path])
    text_entities = milvus_api.generate_entities(text_features, [text])

    if not (milvus_api.insert_milvus(image_entities, _COLLECTION_NAME) and
            milvus_api.insert_milvus(text_entities, _COLLECTION_NAME)):
        _logger.warn("Image+Text memory insertion failed")
        raise MilvusException(message="Image+Text memory insertion failed")


def search_texts_by_similarity(text: str, top_k: int = 1) -> list:
    """
    Search for the most similar text(s) in the collection.
    :param text: The input text to search similar content.
    :param top_k: Number of top similar texts to return.
    :return: List of top_k similar texts.

    throws: MilvusException
    """
    try:
        text_features = local_clip.get_text_features(text)
        context = milvus_api.query_milvus_show_most_similar(
            _COLLECTION_NAME,
            text_features,
            "embeddings",
            {"metric_type": "IP"},
            top_k=top_k,
            filter_type='text'
        )
        return context if context else []
    except MilvusException as e:
        _logger.exception("Text memory similarity search failed")
        raise e


def search_images_by_similarity(image_frame, top_k: int = 1) -> list:
    """
    Search for the most similar image(s) in the collection.
    :param image_frame: The image to insert.
    :param top_k: Number of top similar images to return.
    :return: List of top_k similar images as OpenCV frames (or empty list if failed).

    throws: MilvusException
    """
    try:
        # Generate image embeddings and search for top_k similar images
        image_features = local_clip.get_image_features(image_utility.get_pil_image(image_frame))
        context = milvus_api.query_milvus_show_most_similar(
            _COLLECTION_NAME,
            image_features,
            "embeddings",
            {"metric_type": "IP"},
            top_k=top_k,
            # filter_type='image'
        )

        similar_images = []
        for image_path in context:
            if format_utility.is_binary_data(image_path):
                similar_images.append(image_utility.load_raw_bytes_to_opencv_frame(image_path))
            elif image_path:
                similar_images.append(image_utility.load_image_to_opencv_frame(image_path))

        return similar_images
    except MilvusException as e:
        _logger.exception("Image memory similarity search failed")
        raise e


def search_matching_images(input_text: str, top_k: int = 5) -> list:
    """
    Search for the most similar images in the collection based on input text.
    :param input_text: The text to use for searching similar images.
    :param top_k: Number of top similar images to return.
    :return: List of top_k similar images as OpenCV frames.
    """
    try:
        text_features = local_clip.get_text_features(input_text)

        # Query Milvus for similar images with filter_type='image' to get only images
        similar_images = milvus_api.query_milvus_show_most_similar(
            _COLLECTION_NAME,
            text_features,
            "embeddings",
            {"metric_type": "IP"},
            top_k=top_k,
            filter_type='image'
        )

        # Convert results to OpenCV frames for all supported image formats
        image_results = []
        for image_path in similar_images:
            try:
                if format_utility.is_binary_data(image_path):
                    image_results.append(image_utility.load_raw_bytes_to_opencv_frame(image_path))
                elif image_path:
                    image_results.append(image_utility.load_image_to_opencv_frame(image_path))
            except Exception as e:
                _logger.warning("Failed to load image for path {image_path}: {e}", image_path=image_path, e=e)

        return [img for img in image_results if isinstance(img, np.ndarray)]

    except MilvusException as e:
        _logger.exception("Image similarity search based on text failed")
        raise e
