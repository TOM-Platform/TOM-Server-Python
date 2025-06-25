"""
This script is responsible for the OpenAI general query of LangChain.
It allows users to query the model with image and prompt to get a
general output
API docs: https://platform.openai.com/docs/api-reference
"""
from os import environ

from langchain_openai import ChatOpenAI

import base_keys
from APIs.langchain_llm.langchain_base_client import BaseLLMClient
from Utilities import file_utility, logging_utility
from Utilities.file_utility import get_credentials_file_path

KEY_OPENAI_API = 'openai_api_key'
OPENAI_CREDENTIAL_FILE = get_credentials_file_path(base_keys.OPENAI_CREDENTIAL_FILE_KEY_NAME)

_logger = logging_utility.setup_logger(__name__)


def _set_api_key():
    _logger.info('Setting OpenAI credentials')
    credential = file_utility.read_json_file(OPENAI_CREDENTIAL_FILE)
    # The LangChain/OpenAi Library looks for this "OPENAI_API_KEY" in
    # the environment variable by default
    environ["OPENAI_API_KEY"] = credential[KEY_OPENAI_API]


class OpenAIClient(BaseLLMClient):
    """
    This class is responsible for the OpenAI general query of LangChain.
    It inherits common functionality from BaseLLMClient.
    """

    def __init__(self, temperature: float = 0.3, model: str = "gpt-4o-mini") -> None:
        """
        Parameters
        ________
        temperature: float
            Takes in a value between 0 and 1 inclusive
        model: str
            Takes in a string model. By default, it uses gpt-4o-mini
        """
        super().__init__(temperature, model)
        _set_api_key()
        _logger.info('Starting OpenAIClient ({model})...', model=model)
        self.llm = ChatOpenAI(model=model, temperature=temperature)
