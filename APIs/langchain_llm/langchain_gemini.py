'''
This script is responsible for the Gemini general query of LangChain.
It allows users to query the model with image and prompt to get a
general output.
API docs: https://ai.google.dev/gemini-api/docs
'''
from os import environ
from typing import Any

from langchain.schema.messages import AIMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

import base_keys
from Utilities import file_utility, image_utility, logging_utility

KEY_GEMINI_API = "gemini_api_key"
GEMINI_CREDENTIAL_FILE = file_utility.get_credentials_file_path(base_keys.GEMINI_CREDENTIAL_FILE_KEY_NAME)

_logger = logging_utility.setup_logger(__name__)


def _set_api_key():
    '''
    This function sets the API key.
    '''
    _logger.info('Setting GEMINI credentials')
    credential = file_utility.read_json_file(GEMINI_CREDENTIAL_FILE)
    # The Langchain/Gemini Library looks for this "GOOGLE_API_KEY" in
    # the environment variable by default
    environ["GOOGLE_API_KEY"] = credential[KEY_GEMINI_API]


class GeminiClient:
    '''
    This class is responsible for the Gemini general query of LangChain.
    Attributes
    _________
    llm: ChatGoogleGenerativeAI
        A class object representing langchain LLM model of Gemini
    Methods
    _________
    generate_response(prompt, user_input)
        Generates a response based on prompt and user_input
    generate(user_prompt, image_png_bytes, system_context)
        Generates a response based on image_png_bytes and prompt
    '''

    def __init__(self, temperature: float = 0.3, model: str = "gemini-1.5-flash") -> None:
        '''
        Parameters
        ________
        temperature: float
            Takes in a value between 0 and 1 inclusive
        model: str
            Takes in a string model. By default, it uses gemini flash
        '''
        _set_api_key()
        _logger.info('Starting GeminiClient ({model})...', model=model)
        self.llm = ChatGoogleGenerativeAI(model=model, temperature=temperature)

    def generate_response(self, prompt: str, user_input: Any = None) -> str:
        '''
        This function generates a string response based prompt
        and user_input
        Parameters
        ________
        prompt: str
            Takes in user template in the form of string.
            i.e. What is the translation of {user_input} in French.
        user_input: Any
            Gives the context to the AI by providing a context
            i.e. user_input = "Apple" will format the prompt to become 'What is the translation of Apple in French.'
        Returns
        ________
        str
            A string of model output
        '''
        return self.generate(prompt.format(input=user_input))

    def generate(self, user_prompt: str, image_png_bytes: bytes = bytes(),
                 system_context: str = "You are an advanced helping assistant in "
                                       "answering questions based on given image or text information.") -> str:
        '''
        This function generates a string response based on image_png_bytes
        , user_prompt and system_context
        Parameters
        ________
        user_prompt: str
            Takes in user prompt in the form of string
        image_png_bytes: bytes
            Takes in a PNG image in the form of bytes
        system_context: str
            Gives the system role to the AI by providing a context
            i.e. "You are a chatbot"
        Returns
        ________
        str
            A string of model output
        '''
        system_message = AIMessage(content=system_context)
        if image_png_bytes == bytes():
            human_message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": user_prompt
                    }
                ]
            )
        else:
            base64_img = image_utility.get_base64_image(image_png_bytes)
            human_message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": user_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url":
                                f"data:image/png;base64,{base64_img}"
                        }
                    }
                ]
            )
        messages = [system_message, human_message]
        res = self.llm.invoke(messages).content.strip()
        _logger.debug(res)
        return res
