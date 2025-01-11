'''
This module is used to interact with Google Cloud Vision API.
'''
from google.cloud import vision
from Utilities import image_utility, logging_utility

_logger = logging_utility.setup_logger(__name__)


class VisionClient:
    '''
    This class is responsible for the Google Cloud Vision API.
    '''

    def __init__(self):
        '''
        This method initializes the Google Cloud Vision API.
        '''
        self.client = vision.ImageAnnotatorClient()

    # return a [descriptions, scores, vertices] list
    def _detect_text_image(self, google_vision_image):
        _logger.info("_detect_text_image")
        response = self.client.text_detection(image=google_vision_image)
        annotations = response.text_annotations
        _logger.info("Texts: ", annotations)

        descriptions = []
        scores = []
        vertices = []

        for annotation in annotations:
            descriptions.append(annotation.description)
            scores.append(annotation.score)
            vertices.append(annotation.bounding_poly.vertices)

        if response.error.message:
            raise ValueError(f"{response.error.message}\nFor more info on error messages, "
                             f"check: https://cloud.google.com/apis/design/errors")

        return descriptions, scores, vertices

    def detect_text_image_bytes(self, image_bytes: bytes):
        '''
        This method detects text in an image using text detection.
        Parameters
        ----------
        image_bytes: bytes
            The image bytes to detect text
        '''
        image = vision.Image(content=image_bytes)
        return self._detect_text_image(image)

    def detect_text_image_file(self, image_path: str):
        '''
        This method detects text in an image using text detection.
        Parameters
        ----------
        image_path: str
            The image path to detect text
        '''
        return self.detect_text_image_bytes(image_utility.read_image_file_bytes(image_path))

    def detect_text_image_uri(self, uri: str):
        '''
        This method detects text in an image using text detection.
        Parameters
        ----------
        uri: str
            The image uri to detect text
        '''
        image = vision.Image()
        image.source.image_uri = uri
        return self._detect_text_image(image)

    def detect_text_frame(self, opencv_frame):
        '''
        This method detects text in an image using text detection.
        Parameters
        ----------
        opencv_frame: numpy.ndarray
            The opencv frame to detect text
        '''
        image_content = image_utility.get_png_image_bytes(opencv_frame)
        image = vision.Image(content=image_content)
        return self._detect_text_image(image)

    # detect text in a image using document text detection
    def detect_dense_text(self, image_path: str):
        """
        Detects document features in an image.
        Parameters
        ----------
        image_path: str
            The image path to detect text
        """
        image = vision.Image(content=image_utility.read_image_file_bytes(image_path))
        response = self.client.document_text_detection(image=image)
        for page in response.full_text_annotation.pages:
            for block in page.blocks:
                _logger.info(f'\nBlock confidence: {block.confidence}\n')
                for paragraph in block.paragraphs:
                    _logger.info(f'Paragraph confidence: {paragraph.confidence}')

                    for word in paragraph.words:
                        word_text = ''.join([symbol.text for symbol in word.symbols])
                        _logger.info(f'Word text: {word_text}        (confidence: {word.confidence})')

    # FIXME: extract lower methods, detect_landmarks_image_bytes,
    # detect_landmarks_image_file
    # detect landmarks in a image
    def detect_landmarks(self, image_path: str):
        """
        Detects landmarks in the file.
        Parameters
        ----------
        image_path: str
            The image path to detect landmarks
        """
        image = vision.Image(content=image_utility.read_image_file_bytes(image_path))
        response = self.client.landmark_detection(image=image)
        landmarks = response.landmark_annotations
        descriptions = []
        scores = []
        bounding_boxes = []
        for landmark in landmarks:
            descriptions.append(landmark.description)
            scores.append(landmark.score)
            bounding_boxes.append(landmark.bounding_poly.vertices)

        return descriptions, scores, bounding_boxes

    def detect_objects(self, image_path: str):
        """
        Detects objects in the file.
        Parameters
        ----------
        image_path: str
            The image path to detect objects
        """
        image = vision.Image(content=image_utility.read_image_file_bytes(image_path))
        objects = self.client.object_localization(image=image).localized_object_annotations
        descriptions = []
        scores = []
        bounding_boxes = []

        for object_ in objects:
            descriptions.append(object_.name)
            scores.append(object_.score)
            bounding_boxes.append(object_.bounding_poly.vertices)

        return descriptions, scores, bounding_boxes

    def detect_objects_texts(self, image_bytes: bytes):
        """
        Detects labels in the file.
        Parameters
        ----------
        image_bytes: bytes
            The image bytes to detect objects and texts
        """
        image = vision.Image(content=image_bytes)

        request = {
            "image": image,
            "features": [
                {"type_": vision.Feature.Type.TEXT_DETECTION},
                {"type_": vision.Feature.Type.OBJECT_LOCALIZATION},
            ],
        }

        response = self.client.annotate_image(request)
        _logger.info(response)

        descriptions = []
        scores = []
        bounding_boxes = []
        types = []

        for object_localization in response.localized_object_annotations:
            descriptions.append(object_localization.name)
            scores.append(object_localization.score)
            bounding_boxes.append(object_localization.bounding_poly.vertices)
            types.append("object")

        for text in response.text_annotations:
            descriptions.append(text.description)
            scores.append(text.score)
            bounding_boxes.append(text.bounding_poly.vertices)
            types.append("text")

        return descriptions, scores, bounding_boxes, types

    def detect_objects_landmarks(self, image_bytes: bytes):
        """
        Detects objects and landmarks in the file, excluding text.
        Parameters
        ----------
        image_bytes: bytes
            The image bytes to detect objects and landmarks
        """

        image = vision.Image(content=image_bytes)

        request = {
            "image": image,
            "features": [
                {"type_": vision.Feature.Type.OBJECT_LOCALIZATION},
                {"type_": vision.Feature.Type.LANDMARK_DETECTION},
            ],
        }

        response = self.client.annotate_image(request)

        descriptions = []
        scores = []
        bounding_boxes = []
        types = []

        for object_localization in response.localized_object_annotations:
            descriptions.append(object_localization.name)
            scores.append(object_localization.score)
            bounding_boxes.append(object_localization.bounding_poly.vertices)
            types.append("object")

        for landmark in response.landmark_annotations:
            descriptions.append(landmark.description)
            scores.append(landmark.score)
            bounding_boxes.append(landmark.bounding_poly.vertices)
            types.append("landmark")

        return descriptions, scores, bounding_boxes, types
