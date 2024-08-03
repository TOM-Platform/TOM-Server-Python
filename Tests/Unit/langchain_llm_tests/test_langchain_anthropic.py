'''
This file contains the unit tests for the Anthropic class.
'''
from Utilities import image_utility
from APIs.langchain_llm.langchain_anthropic import AnthropicClient


def test_langchain_openai_with_input():
    ''''
    Test with inputs
    '''
    assert AnthropicClient(0).generate_response(
        "What is the Spanish translation of {input}? Provide only the \
            answer. Please do not add punctuation. Ensure first letter is \
                capitalised. Ensure there is \
                only one word for this prompt.",
        "Apple") == "Manzana"


def test_langchain_openai_without_input():
    '''
    Test without inputs
    '''
    assert AnthropicClient(0).generate_response(
        "What is the Spanish translation of Apple? \
            Provide only the direct translation of the answer. Please do not \
                add punctuation. \
                    Ensure first letter is capitalised. \
                        Ensure there is only one word \
                            for this prompt.") == "Manzana"


def test_langchain_llm_without_image():
    '''
    This function tests the AnthropicClient class without image.
    '''
    assert AnthropicClient(0).generate(
        "What is the Spanish translation of Apple? \
            Provide only the direct translation of the \
                answer. Please do not add punctuation. \
                    Ensure first letter is capitalised. \
                        Ensure there is only one word for \
                            this prompt.") == "Manzana"


def test_langchain_llm_with_image():
    '''
    This function tests the AnthropicClient class with image.
    '''
    image_bytes = image_utility.read_image_url_bytes(
        'https://pngimg.com/d/apple_PNG12504.png')
    assert AnthropicClient(0).generate(
        "What is the Spanish translation of given image? \
            Provide only the direct translation of answer. \
                Please do not add punctuation. \
                    Ensure first letter is capitalised. \
                        Ensure there is only one word for \
                            this prompt.",
        image_bytes
    ) == "Manzana"
