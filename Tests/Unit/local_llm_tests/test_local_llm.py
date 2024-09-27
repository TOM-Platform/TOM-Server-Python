# coding=utf-8
import pytest

from APIs.local_llm.local_llm import generate_text, generate_text_with_history


def test_local_llm_generate_text():
    user_prompt: str = "What is the capital of France?"
    system_prompt: str = "You are a friendly chatbot."
    response: str = generate_text(user_prompt, system_prompt).replace("\n", "")
    assert response == 'Paris.' or response == 'The capital of France is Paris.'


def test_local_llm_generate_text_with_history():
    user_prompt: str = "What was my previous question?"
    system_prompt: str = "You are a friendly chatbot."
    response: str = generate_text_with_history(user_prompt,
                                               [{"role": "user", "content": "What is the capital of France?"}],
                                               system_prompt).replace("\n", "")

    assert response == 'Your previous question was: "What is the capital of France?"'
