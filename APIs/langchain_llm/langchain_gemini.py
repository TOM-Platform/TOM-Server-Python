"""
This script is responsible for the Gemini general query of LangChain.
It allows users to query the model with image and prompt to get a
general output.
API docs: https://ai.google.dev/gemini-api/docs
"""
from os import environ

from langchain_google_genai import ChatGoogleGenerativeAI

import base_keys
from APIs.langchain_llm.langchain_base_client import BaseLLMClient
from Utilities import file_utility, logging_utility
from Utilities.file_utility import get_credentials_file_path

KEY_GEMINI_API = "gemini_api_key"
GEMINI_CREDENTIAL_FILE = get_credentials_file_path(base_keys.GEMINI_CREDENTIAL_FILE_KEY_NAME)

_logger = logging_utility.setup_logger(__name__)


def _set_api_key():
    """
    This function sets the API key.
    """
    _logger.info('Setting GEMINI credentials')
    credential = file_utility.read_json_file(GEMINI_CREDENTIAL_FILE)
    # The Langchain/Gemini Library looks for this "GOOGLE_API_KEY" in
    # the environment variable by default
    environ["GOOGLE_API_KEY"] = credential[KEY_GEMINI_API]


class GeminiClient(BaseLLMClient):
    """
    This class is responsible for the Gemini general query of LangChain.
    It inherits common functionality from BaseLLMClient.
    """

    def __init__(self, temperature: float = 0.3, model: str = "gemini-2.0-flash") -> None:
        """
        Parameters
        ________
        temperature: float
            Takes in a value between 0 and 1 inclusive
        model: str
            Takes in a string model. By default, it uses gemini-2.0-flash
        """
        super().__init__(temperature, model)
        _set_api_key()
        _logger.info('Starting GeminiClient ({model})...', model=model)
        self.llm = ChatGoogleGenerativeAI(model=model, temperature=temperature)
