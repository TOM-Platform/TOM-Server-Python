'''
This file is to test openai langchain
'''
from APIs.langchain_llm.langchain_openai import OpenAIClient
from Utilities import image_utility
from pydantic import BaseModel
import pytest


def test_langchain_llm_with_input():
    ''''
    Test with inputs
    '''
    assert OpenAIClient(0).generate_response(
        "What is the Spanish translation of {input}? Provide only the \
            answer. Please do not add punctuation. Ensure first letter is \
                capitalised. Ensure there is \
                only one word for this prompt.",
        "Apple") == "Manzana"


def test_langchain_llm_without_input():
    '''
    Test without inputs
    '''
    assert OpenAIClient(0).generate_response(
        "What is the Spanish translation of Apple? \
            Provide only the direct translation of the answer. Please do not \
                add punctuation. \
                    Ensure first letter is capitalised. \
                        Ensure there is only one word \
                            for this prompt.") == "Manzana"


def test_langchain_llm_without_image():
    '''
    This function tests the OpenAIClient class without image.
    '''
    assert OpenAIClient(0).generate(
        "What is the Spanish translation of Apple? \
            Provide only the direct translation of the \
                answer. Please do not add punctuation. \
                    Ensure first letter is capitalised. \
                        Ensure there is only one word for \
                            this prompt.") == "Manzana"

def test_langchain_llm_with_image():
    '''
    This function tests the OpenAIClient class with image.
    '''
    image_bytes = image_utility.read_image_url_bytes(
        'https://pngimg.com/d/apple_PNG12504.png')
    assert OpenAIClient(0).generate(
        "What is the Spanish translation of given image? \
            Provide only the direct translation of answer. \
                Please do not add punctuation. \
                    Ensure first letter is capitalised. \
                        Ensure there is only one word for \
                            this prompt.",
        image_bytes
    ) == "Manzana"

def test_generate_structured_output():
    """
    Test OpenAIClient's generate_structured_output method.
    """

    class TranslationOutput(BaseModel):
        """
        Pydantic model for structured output.
        """
        translation: str

    system_prompt = (
        "Provide a structured JSON output for the Spanish translation "
        "of the word 'Apple'. Ensure it matches the template provided."
    )

    response = OpenAIClient(0).generate_structured_output(
        system_prompt=system_prompt,
        template_object=TranslationOutput
    )
    expected_response = TranslationOutput(translation="Manzana")

    assert response == expected_response, f"Expected '{expected_response}', got '{response}'"

