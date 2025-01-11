'''
This script is responsible for the OpenAI general query of LangChain.
It allows users to query the model with image and prompt to get a
general output
API docs: https://platform.openai.com/docs/api-reference
'''
from os import environ
from typing import Any, Optional
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain.schema.messages import AIMessage, HumanMessage, SystemMessage
import base_keys
from Utilities import file_utility, image_utility, logging_utility
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


class OpenAIClient:
    '''
    This class is responsible for the OpenAI general query of LangChain.
    Attributes
    _________
    llm: ChatOpenAI
        A class object representing langchain LLM model
    Methods
    _________
    generate_response(prompt, user_input)
        Generates a response based on prompt and user_input
    generate(user_prompt, image_png_bytes, system_context)
        Generates a response based on image_png_bytes and user_prompt
    '''

    def __init__(self, temperature: float = 0.3, model: str = "gpt-4o-mini") -> None:
        '''
        Parameters
        ________
        temperature: float
            Takes in a value between 0 and 1 inclusive
        model: str
            Takes in a string model. By default, it uses gpt-4o
        '''
        _set_api_key()
        _logger.info('Starting OpenAIClient ({model})...', model=model)
        self.llm = ChatOpenAI(model=model, temperature=temperature, )

    def generate_response(self, prompt, user_input: Any = None) -> str:
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
                 system_context: str = "You are an advanced helping assistant in answering questions based on given "
                                       "image or text information.") -> str:
        '''
        This function generates a string response based on image_png_bytes
        and user_prompt
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
        return res

    def generate_structured_output(self, system_prompt: str,
                                   template_object: BaseModel,
                                   input_text: Optional[str] = None,
                                   image_base_64: Optional[str] = None):
        """
        Generate structured JSON output based on a given PromptTemplate.

        Args:
            system_prompt (str): System message for the LLM.
            template_object (BaseModel): Model for output parsing.
            input_text (Optional[str]): Text input to be included in the message.
            image_base_64 (Optional[str]): Base64 encoded image string.

        Returns:
            str: JSON dictionary of the LLM output based on the given template.
        """
        template_parser = PydanticOutputParser(pydantic_object=template_object)
        format_instructions = template_parser.get_format_instructions()

        # Build HumanMessage content dynamically based on input_text and image
        human_content = [{"type": "text", "text": format_instructions}]
        if input_text:
            human_content.append({"type": "text", "text": input_text})
        if image_base_64:
            image_url = f"data:image/png;base64,{image_base_64}"
            human_content.append({"type": "image_url", "image_url": {"url": image_url}})

        # Build the ChatPromptTemplate
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_content)
        ])

        # Use the chain operator to combine the prompt and LLM
        chain = prompt | self.llm | template_parser
        result = chain.invoke({})  # Empty input dict since content is already set in the prompt

        return result
