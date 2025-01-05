import json
from typing import Optional, List
import numpy as np
from pydantic import BaseModel, Field
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
from APIs.cloud_vision.VisionClient import VisionClient
from APIs.langchain_llm.llm_exceptions import ErrorClassificationException
from APIs.langchain_llm.langchain_openai import OpenAIClient
from Services.pandalens_service import pandalens_prompt, pandalens_const
from Utilities import image_utility

class LabelCaptionSchema(BaseModel):
    """Schema for labeling and captioning an image."""
    label: str = Field(description="Label for the image")
    caption: str = Field(description="Generated caption for the image")

class AuthoringSchema(BaseModel):
    """Schema for generating travel blog content."""
    summary: str = Field(description="Snippet of the travel blog content in first-person narration")
    question: Optional[str] = Field(description="Reflective question for blog improvement.")

class BloggingSchema(BaseModel):
    """Schema for creating a blog with intro, indexes, and conclusion."""
    intro: str = Field(description="Generated blog introduction")
    indexes: List[int] = Field(description="A list of relevant indexes")
    conclusion: str = Field(description="Generated blog conclusion")

class PandaLensAI:
    """Wrapper class for AI functionalities in PandaLens."""
    MAX_QUESTIONS = 2

    def __init__(self) -> None:
        self.llm = OpenAIClient(temperature=0.7)
        self.image_processor = VisionClient()
        self.memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True, input_key="human_input"
        )
        self.asked_questions = set()
        self.session_data = {}

    def _add_to_memory(self, role: str, content: str):
        """Add messages to the conversation memory."""
        message_class = HumanMessage if role == "human" else AIMessage
        self.memory.chat_memory.add_message(message_class(content=content))

        # Track questions if added by the AI
        if role != "human":
            self.asked_questions.add(content.strip())

    def _get_memory_context(self) -> str:
        """Retrieve the formatted conversation history."""
        messages = self.memory.chat_memory.messages
        if not messages:
            return ""

        history = "\nPrevious conversation:\n"
        for msg in messages:
            role = "User" if isinstance(msg, HumanMessage) else "You"
            history += f"{role}: {msg.content}\n"

        # Add a reminder to avoid duplicate questions
        if self.asked_questions:
            history += "\nNote: Avoid asking the following questions again:\n"
            history += "\n".join(f"- {q}" for q in self.asked_questions)

        return history

    def _prepare_human_message(self, label: str, caption: str, ocr_text: str, user_action: str) -> str:
        """Construct the human message for the LLM."""
        message = {
            "description": [
                {
                    "photo_label": label,
                    "photo_caption": caption,
                    "ocr": ocr_text,
                    "background_audio": None,
                    "user_action": user_action,
                    "user_voice_transcription": None
                }
            ]
        }
        return json.dumps(message)

    def generate_question(self, image_array, user_action):
        """Generate a reflective question and summary based on the image."""
        img_bytes = image_utility.get_png_image_bytes(image_array)
        ocr_text = self.get_ocr_text(img_bytes)
        label, caption = self.get_label_and_caption(img_bytes)

        self.session_data.update({
            "last_image_label": label,
            "last_image_caption": caption,
            "last_ocr_text": ocr_text
        })

        human_message = self._prepare_human_message(label, caption, ocr_text, user_action)
        memory_context = self._get_memory_context()

        json_output = self.llm.generate_structured_output(
            system_prompt=pandalens_prompt.PANDALENS_CONTEXT + "\n" + memory_context,
            template_object=AuthoringSchema,
            input_text=human_message
        )

        self._add_to_memory("human", f"Analyzed image with label: {label}")
        self._add_to_memory("ai", json.dumps(json_output.dict()))
        print(len(self.asked_questions))

        if len(self.asked_questions) > self.MAX_QUESTIONS:
            return pandalens_const.LLM_NO_QUESTIONS, json_output.summary

        return json_output.question, json_output.summary

    def get_label_and_caption(self, image_bytes):
        """Retrieve the label and caption for the given image."""
        if not image_bytes:
            raise ValueError("Image bytes cannot be None or empty.")

        base64_img = image_utility.get_base64_image(image_bytes)
        json_output = self.llm.generate_structured_output(
            system_prompt=pandalens_prompt.IMAGE_CLASSIFIER_CONTEXT,
            template_object=LabelCaptionSchema,
            image_base_64=base64_img
        )

        return json_output.label, json_output.caption

    def get_ocr_text(self, image_bytes):
        """Perform OCR on the image bytes."""
        if not image_bytes:
            raise ErrorClassificationException("Image bytes cannot be none or empty")

        text_contents, scores, _ = self.image_processor.detect_text_image_bytes(image_bytes)
        if scores:
            max_index = np.argmax(scores)
            return text_contents[max_index]
        return None

    def generate_intro_conclusion(self, speech: str, moments: str):
        """Generate blog introduction, indexes, and conclusion."""
        human_message = f"{moments}\n{speech}"
        json_output = self.llm.generate_structured_output(
            system_prompt=pandalens_prompt.PANDALENS_BLOGGING_CONTEXT,
            template_object=BloggingSchema,
            input_text=json.dumps(human_message)
        )

        return json_output.intro, json_output.conclusion, json_output.indexes

    def clear_chat_history(self):
        """Clear the chat history and session data."""
        self.memory.clear()
        self.session_data.clear()
        self.asked_questions.clear()
