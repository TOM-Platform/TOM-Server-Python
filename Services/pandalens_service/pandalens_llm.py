import json
from typing import Optional, List, Tuple, Any, Dict

from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
from pydantic import BaseModel, Field

import tenacity
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import requests.exceptions

from APIs.langchain_llm.langchain_openai import OpenAIClient
from Services.pandalens_service import pandalens_prompt, pandalens_const
from Utilities import image_utility, logging_utility

_logger = logging_utility.setup_logger(__name__)


class AuthoringSchema(BaseModel):
    """Schema for all in-situ vision and content tasks."""
    label: str = Field(description="Primary label for the image")
    caption: str = Field(description="Natural, descriptive summary of the image scene")
    ocr_text: Optional[str] = Field(description="Any text found visually in the image")
    summary: str = Field(description="First-person blog-style summary of the moment")
    identifier: str = Field(description="A single phrase description which help users to recall the moment")
    user_question: Optional[str] = Field(description="Any questions raised by the user")
    answer_to_user: Optional[str] = Field(description="Brief answer to the question raised by the user")
    reflective_system_question: Optional[str] = Field(description="Reflective question to deepen the narrative")


class BloggingSchema(BaseModel):
    """Schema for creating a fully coherent blog."""
    indexes: List[int] = Field(description="List of selected moment indexes")
    enhanced_summaries: List[str] = Field(description="Refined summaries for each selected moment")
    introduction: str = Field(description="Generated blog introduction")
    conclusion: str = Field(description="Generated blog conclusion")


# Custom retry logic for LLM API calls
def _is_server_error_or_timeout(exception):
    """Check if the exception is a server error or timeout."""
    if isinstance(exception, requests.exceptions.HTTPError):
        # Check for 5xx server errors
        return 500 <= exception.response.status_code < 600

    if isinstance(exception, requests.exceptions.Timeout):
        # Timeout errors
        return True

    if "overloaded" in str(exception).lower():
        # Server overload errors
        return True

    return False


class PandaLensAI:
    """Wrapper class for AI functionalities in PandaLens."""
    MAX_QUESTIONS = int(pandalens_const.PANDALENS_QUESTION_LIMIT)

    MAX_RETRIES = int(pandalens_const.LLM_REQUEST_MAX_RETRIES)
    BACKOFF_BASE_SECONDS = pandalens_const.LLM_REQUEST_BACKOFF_BASE_SECONDS

    MAX_MEMORY_MESSAGES = int(MAX_QUESTIONS * 2 * 2)

    def __init__(self) -> None:
        self.llm = OpenAIClient(model="gpt-4.1-nano", temperature=pandalens_const.DEFAULT_LLM_TEMPERATURE)
        self.memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True, input_key="human_input"
        )
        self.asked_system_questions = set()

    def _add_to_memory(self, role: str, content: str):
        """Add messages to the conversation memory."""
        message_class = HumanMessage if role == "human" else AIMessage
        self.memory.chat_memory.add_message(message_class(content=content))

        if len(self.memory.chat_memory.messages) > self.MAX_MEMORY_MESSAGES:
            self.memory.chat_memory.messages.pop(0)  # Remove oldest

    def _get_memory_context(self) -> str:
        """Retrieve the formatted conversation history."""
        messages = self.memory.chat_memory.messages
        if not messages:
            return ""

        history = "\nPrevious conversation history::\n"
        for msg in messages:
            role = "User" if isinstance(msg, HumanMessage) else "You"
            history += f"{role}: {msg.content}\n"

        return history

    @staticmethod
    def _encode_image(image_array: Any) -> str:
        """Convert a NumPy array to a base64-encoded PNG."""
        png_bytes = image_utility.get_png_image_bytes(image_array)
        return image_utility.get_base64_image(png_bytes)

    @staticmethod
    def _build_human_input(
            user_action: str,
            user_utterance: str,
            ask_followup: bool,
            previous_questions: Tuple[str, ...],
            user_location: Dict[str, Any],
            timestamp: str,
            user_profile: Dict[str, Any],
    ) -> str:
        payload = {
            "user_action": user_action,
            "user_speech": user_utterance,
            "ask_followup_question": ask_followup,
            "previous_system_questions": list(previous_questions),
            "user_location": user_location,
            "time": timestamp,
            "user_profile": user_profile,
        }
        return json.dumps(payload)

    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=BACKOFF_BASE_SECONDS, min=BACKOFF_BASE_SECONDS),
        retry=retry_if_exception_type((
                requests.exceptions.HTTPError,
                requests.exceptions.Timeout,
                Exception
        )) & tenacity.retry_if_exception(_is_server_error_or_timeout),
        before_sleep=lambda retry_state: _logger.warning(
            f"Retrying request (attempt {retry_state.attempt_number}/{PandaLensAI.MAX_RETRIES}) "
            f"after error: {retry_state.outcome.exception()}. "
            f"Waiting {retry_state.next_action.sleep} seconds..."
        ),
        reraise=True
    )
    def generate_moment_response(
            self,
            image_array: Any,
            user_action: str,
            user_utterance: str,
            user_location: Dict[str, Any],
            timestamp: str,
            user_profile: Dict[str, Any]
    ) -> Tuple[Optional[str], Optional[str], str, str]:
        """
        Generate a structured summary of the captured moment.

        Returns a 4-tuple:
          1. identifier: one-sentence description of the moment (or None on first turn)
          2. summary: a brief summary (or None on first turn)
          3. answer_to_user: direct answer to any user question (empty if none)
          4. reflective_system_question: follow-up question to elicit feedback
        """

        # Initial turn: prompt default question
        if not self.asked_system_questions:
            default_q = pandalens_const.LLM_DEFAULT_QUESTION
            self.asked_system_questions.add(default_q)
            return None, None, "", default_q

        # decide whether we can ask another reflective question
        can_ask = len(self.asked_system_questions) < self.MAX_QUESTIONS

        # --- prepare inputs ---
        img_b64 = self._encode_image(image_array)
        human_input = self._build_human_input(
            user_action=user_action,
            user_utterance=user_utterance,
            ask_followup=can_ask,
            previous_questions=tuple(sorted(self.asked_system_questions)),
            user_location=user_location,
            timestamp=timestamp,
            user_profile=user_profile
        )
        memory_context = self._get_memory_context()

        # call the LLM (with retry)
        json_output = self.llm.generate_structured_output(
            system_prompt=f"{pandalens_prompt.IN_SITU_ASSISTANT_CONTEXT}\n{memory_context}",
            template_object=AuthoringSchema,
            input_text=human_input,
            image_base_64=img_b64
        )

        # update memory & state
        self._add_to_memory("human", f"User did: {user_action}, said: {user_utterance}")
        self._add_to_memory("ai", json.dumps(json_output.dict()))
        self.asked_system_questions.add(json_output.reflective_system_question)

        return (
            json_output.identifier,
            json_output.summary,
            json_output.answer_to_user,
            json_output.reflective_system_question
        )

    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=BACKOFF_BASE_SECONDS, min=BACKOFF_BASE_SECONDS),
        retry=retry_if_exception_type((
                requests.exceptions.HTTPError,
                requests.exceptions.Timeout,
                Exception
        )) & tenacity.retry_if_exception(_is_server_error_or_timeout),
        before_sleep=lambda retry_state: _logger.warning(
            f"Retrying request (attempt {retry_state.attempt_number}/{PandaLensAI.MAX_RETRIES}) "
            f"after error: {retry_state.outcome.exception()}. "
            f"Waiting {retry_state.next_action.sleep} seconds..."
        ),
        reraise=True
    )
    def generate_summaries_introduction_conclusion(self, moments: list[dict], speech: str, user_profile: dict):
        """
        Generate a complete, coherent blog with enhanced summaries for selected moments.

        Args:
            moments: a list of dictionary of stored moments
            speech: User dictated speech about moments to include
            user_profile: dictionary of user profile

        Returns:
            indexes: List of moment indexes to include
            enhanced_summaries: List of rewritten summaries for each selected moment
            introduction: Blog introduction
            conclusion: Blog conclusion
        """

        human_message = json.dumps({
            "moments": moments,
            "user_instructions": speech,
            "user_profile": user_profile,
        })

        json_output = self.llm.generate_structured_output(
            system_prompt=pandalens_prompt.BLOGGING_ASSISTANT_CONTEXT,
            template_object=BloggingSchema,
            input_text=human_message
        )

        return (
            json_output.indexes,
            json_output.enhanced_summaries,
            json_output.introduction,
            json_output.conclusion
        )

    def clear_chat_history(self):
        """Clear the chat history and session data."""
        self.memory.clear()
        self.asked_system_questions.clear()
