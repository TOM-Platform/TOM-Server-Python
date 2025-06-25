"""
This script is responsible for the Anthropic general query of LangChain.
It allows users to query the model with image and prompt to get a
general output.
API docs: https://docs.anthropic.com/claude/docs/intro-to-claude
"""
from os import environ

from langchain_anthropic import ChatAnthropic

import base_keys
from APIs.langchain_llm.langchain_base_client import BaseLLMClient
from Utilities import file_utility, logging_utility
from Utilities.file_utility import get_credentials_file_path

KEY_ANTHROPIC_API = 'anthropic_api_key'
ANTHROPIC_CREDENTIAL_FILE = get_credentials_file_path(base_keys.ANTHROPIC_CREDENTIAL_FILE_KEY_NAME)

_logger = logging_utility.setup_logger(__name__)


def _set_api_key():
    _logger.info('Setting Anthropic credentials')
    credential = file_utility.read_json_file(ANTHROPIC_CREDENTIAL_FILE)
    # The Langchain/Anthropic Library looks for this "ANTHROPIC_API_KEY" in
    # the environment variable by default
    environ["ANTHROPIC_API_KEY"] = credential[KEY_ANTHROPIC_API]


class AnthropicClient(BaseLLMClient):
    """
    This class is responsible for the Anthropic general query of LangChain.
    It inherits common functionality from BaseLLMClient.
    """

    def __init__(self, temperature: float = 0.3, model: str = 'claude-3-5-haiku-latest') -> None:
        """
        Parameters
        ________
        temperature: float
            Takes in a value between 0 and 1 inclusive
        model: str
            Takes in a string model. By default, it uses claude-3-5-haiku-latest
        """
        super().__init__(temperature, model)
        _set_api_key()
        _logger.info('Starting Anthropic ({model})...', model=model)
        self.llm = ChatAnthropic(model=model, temperature=temperature)
