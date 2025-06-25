from pydantic import BaseModel, Field
from APIs.langchain_llm.langchain_gemini import GeminiClient
from Utilities import image_utility
from .aiget_service_config import AigetConfig


class AnswerSchema(BaseModel):
    """Schema for answering questions based on user questions."""

    answer: str = Field(description="The answer for the question based on Task 1")
    summarized_answer: str = Field(description="The summarized version of the response, including emojis")


class KnowledgeContentSchema(BaseModel):
    """Schema for generating content based on user questions."""

    aiget_content: str = Field(description="The AI-generated suggestion based on Task 1.")
    summarized_content: str = Field(description="The summarized version of the AI suggestion, including emojis.")


class AigetAI:
    """
    This class is responsible for generating content/answers based on prompts/user questions.
    It uses the GeminiClient to interact with the Gemini LLM.
    """

    def __init__(self) -> None:
        self.llm = GeminiClient(temperature=0.3, model="gemini-1.5-flash")

    def generate_answers(self, user_prompt: str, image_png_bytes: bytes = bytes())-> tuple[str, str]:
        """
        Generate answers based on the user questions and image data.
        Args:
            user_prompt (str): The user's prompt or question.
            image_png_bytes (bytes): The image data in PNG format.
        Returns:
            tuple: A tuple containing the answer and summarized answer.
        """

        # If image data is provided, encode it to base64
        if image_png_bytes:
            image_base64 = image_utility.get_base64_image(image_png_bytes)
        else:
            image_base64 = None

        # Call the LLM to generate the structured output
        json_output = self.llm.generate_structured_output(
            system_prompt=AigetConfig.QUESTION_PROMPT,
            template_object=AnswerSchema,
            input_text=user_prompt,
            image_base_64=image_base64
        )

        return (json_output.answer, json_output.summarized_answer)

    def generate_content(self, user_prompt: str, image_png_bytes: bytes = bytes())-> tuple[str, str]:
        """
        Generate content based on the user prompt and image data.
        Args:
            user_prompt (str): The user's prompt or question.
            image_png_bytes (bytes): The image data in PNG format.
        Returns:
            tuple: A tuple containing the content and summarized content.
        """

        # If image data is provided, encode it to base64
        if image_png_bytes:
            image_base64 = image_utility.get_base64_image(image_png_bytes)
        else:
            image_base64 = None

        # Call the LLM to generate the structured output
        json_output = self.llm.generate_structured_output(
            system_prompt=AigetConfig.SYSTEM_PROMPT,
            template_object=KnowledgeContentSchema,
            input_text=user_prompt,
            image_base_64=image_base64
        )

        return (json_output.aiget_content, json_output.summarized_content)
