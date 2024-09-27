import json
import numpy as np
from APIs.cloud_vision.VisionClient import VisionClient
from APIs.langchain_llm.langchain_openai import OpenAIClient
from Services.pandalens_service import pandalens_prompt, pandalens_const
from Services.pandalens_service.pandalens_exceptions import ErrorClassificationException
from Utilities import image_utility


class PandaLensAI:
    """
    This class handles the AI-related functionalities for the PandaLens service.
    It interacts with external APIs to process images and generate text-based responses 
    based on user actions or input data.
    """

    def __init__(self) -> None:
        self.llm = OpenAIClient()
        self.image_processor = VisionClient()
        self.chat = "Human: " + pandalens_prompt.PANDALENS_CONTEXT
        self.question_count = 0

    def get_first_generated_response(self, image_array, user_action):
        img_byte = image_utility.get_png_image_bytes(image_array)
        ocr_text = self.get_ocr_text(img_byte)
        label, caption = self.get_label_and_caption(img_byte)

        human_message = {
            "image": [
                {
                    "photo_label": label,
                    "photo_caption": caption,
                    "ocr": ocr_text,
                    "background_audio": None,
                    "user_behavior": user_action,
                    "user_voice_transcription": None
                }
            ]
        }
        response = self.llm.generate(user_prompt=json.dumps(human_message), system_context=self.chat)
        self.chat = "Human: " + pandalens_prompt.PANDALENS_CONTEXT
        self._temporary_memory_build(human_message, response)
        extracted_json = self._extract_json_data(response)
        json_map = json.loads(extracted_json)
        question = json_map[pandalens_const.LLM_JSON_AUTHORING_RESPONSE_QUESTION_KEY]
        summary = json_map[pandalens_const.LLM_JSON_AUTHORING_RESPONSE_SUMMARY_KEY]
        return question, summary

    def get_subsequent_generated_response(self, human_message):
        self.question_count += 1
        response = self.llm.generate(user_prompt=json.dumps(human_message), system_context=self.chat)
        self._temporary_memory_build(human_message, response)
        extracted_json = self._extract_json_data(response)
        json_map = json.loads(extracted_json)
        if self.question_count == pandalens_const.PANDALENS_QUESTION_LIMIT:
            question = pandalens_const.LLM_NO_QUESTIONS
        else:
            question = json_map[pandalens_const.LLM_JSON_AUTHORING_RESPONSE_QUESTION_KEY]
        summary = json_map[pandalens_const.LLM_JSON_AUTHORING_RESPONSE_SUMMARY_KEY]
        return question, summary

    def get_label_and_caption(self, image_bytes):
        response = self.llm.generate(user_prompt="", image_png_bytes=image_bytes,
                                     system_context=pandalens_prompt.IMAGE_CLASSIFIER_CONTEXT)
        extracted_json = self._extract_json_data(response)
        json_map = json.loads(extracted_json)
        label = json_map['label']
        caption = json_map['caption']
        return label, caption

    def get_ocr_text(self, image_bytes):
        if image_bytes is None or image_bytes == "":
            raise ErrorClassificationException("Image string cannot be none or empty")

        text_contents, scores, _ = self.image_processor.detect_text_image_bytes(image_bytes)
        # # for testing
        # with open("filename.png", 'wb') as image_file:
        #     image_file.write(image_bytes)
        if len(scores) > 0:
            max_index = np.argmax(scores)
            ocr = text_contents[max_index]
            return ocr
        return None

    def _extract_json_data(self, json_response):
        # Expected output of the LLM json structure: ```json{<JSON_CONTENT>}```
        json_extract = json_response[7:len(json_response) - 3]
        return json_extract

    def _temporary_memory_build(self, human, ai):
        human_str = json.dumps(human)
        ai_str = json.dumps(ai)
        self.chat = self.chat + "\nHuman: " + human_str
        self.chat = self.chat + "\nAI: " + ai_str

    def clear_chat_history(self):
        self.chat = "Human: " + pandalens_prompt.PANDALENS_CONTEXT
        self.question_count = 0

    def generate_intro_conclusion(self, speech, moments):
        blogging_context = "Human: " + pandalens_prompt.PANDALENS_BLOGGING_CONTEXT
        human_message = moments + "\n" + speech
        response = self.llm.generate(user_prompt=human_message, system_context=blogging_context)
        extracted_json = self._extract_json_data(response)
        json_map = json.loads(extracted_json)
        intro = json_map[pandalens_const.LLM_JSON_BLOGGING_RESPONSE_INTRO_KEY]
        conclusion = json_map[pandalens_const.LLM_JSON_BLOGGING_RESPONSE_CONCLUSION_KEY]
        return intro, conclusion
