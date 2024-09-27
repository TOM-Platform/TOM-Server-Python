import os
from langchain.output_parsers.openai_tools import JsonOutputToolsParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import base_keys
from Utilities import file_utility, logging_utility
from Utilities.file_utility import get_credentials_file_path

KEY_OPENAI_API = 'openai_api_key'
OPENAI_CREDENTIAL_FILE = get_credentials_file_path(base_keys.OPENAI_CREDENTIAL_FILE_KEY_NAME)

_logger = logging_utility.setup_logger(__name__)


def _set_api_key():
    _logger.info('Setting OpenAI credentials')
    credential = file_utility.read_json_file(OPENAI_CREDENTIAL_FILE)
    # The LangChain/OpenAI Library looks for this "OPENAI_API_KEY" in
    # the environment variable by default
    os.environ["OPENAI_API_KEY"] = credential[KEY_OPENAI_API]


class LangChainNlpOpenAI:
    """
    This class provides an interface to interact with the OpenAI language model using LangChain.
    It sets up the OpenAI API key, initializes a prompt template, and processes natural language
    input to extract structured data or entities.
    """

    def __init__(self, prompt: str, tools: list, temperature: float = 0.3) -> None:
        # load openai credentials
        _set_api_key()
        self.initial_prompt = prompt

        _logger.info('Starting LangChainNlp...')

        # Define the output parser
        self.parser = JsonOutputToolsParser()

        # Define the prompt template
        prompt_template = PromptTemplate(template="{input}", input_variables=["input"])

        self.llm = ChatOpenAI(temperature=temperature).bind_tools(tools)
        self.llm_chain = prompt_template | self.llm | self.parser

    def extract_label_entities(self, input_text: str) -> dict:
        response = self.llm_chain.invoke({"input": input_text})

        return response[0]["args"]
