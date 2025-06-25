from google.cloud import translate_v2 as translate
from Utilities import logging_utility

_logger = logging_utility.setup_logger(__name__)


class TranslationClient:
    """
    A client to handle text translations using Google Cloud Translation API.
    This class provides methods to translate text from one language to another with Google Cloud Translation service.
    """

    def __init__(self):
        self.client = translate.Client()

    # returns [input, translatedText, detectedSourceLanguage]
    def translate_text(self, target: str, text: str) -> dict:
        if isinstance(text, bytes):
            text = text.decode("utf-8")
        # to get the target language codes
        # languages = self.client.get_languages()

        # for language in languages:
        #     _logger.info("{name} ({language})".format(**language))

        result = self.client.translate(text, target_language=target)

        # _logger.info("Text: {}".format(result["input"]))
        # _logger.info("Translation: {}".format(result["translatedText"]))
        # _logger.info("Detected source language: {}".format(result["detectedSourceLanguage"]))

        # FIXME: format in the required format
        return result
