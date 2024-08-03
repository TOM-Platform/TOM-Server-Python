from google.cloud import translate_v2 as translate
import logging


class TranslationClient:
    def __init__(self):
        self.client = translate.Client()
    
    # returns [input, translatedText, detectedSourceLanguage]
    def translate_text(self, target: str, text: str) -> dict:

        if isinstance(text, bytes):
            text = text.decode("utf-8")
        
        # to get the target language codes
        # languages = self.client.get_languages()

        # for language in languages:
        #     logging.info("{name} ({language})".format(**language))

        result = self.client.translate(text, target_language=target)

        # logging.info("Text: {}".format(result["input"]))
        # logging.info("Translation: {}".format(result["translatedText"]))
        # logging.info("Detected source language: {}".format(result["detectedSourceLanguage"]))

        # FIXME: format in the required format
        return result


