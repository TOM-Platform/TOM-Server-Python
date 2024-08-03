import os
import pytest

from APIs.langchain_llm.langchain_nlp_openai import LangChainNlpOpenAI
from Utilities.file_utility import get_project_root, read_prompt
from Services.running_service.langchain_running_command_model import RunningCommand

initial_prompt = read_prompt(os.path.join(get_project_root(), 'Services', 'running_service', 'running_prompt.txt'))
langchainNlpOpenAI = LangChainNlpOpenAI(prompt=initial_prompt, tools=[RunningCommand])


def test_langchain_nlp_walking():
    assert langchainNlpOpenAI.extract_label_entities(
        'Paragraph: Walking to Central Library, Speed Training, 10min/km') == {
               'exercise_type': 'Walking',
               'destination': 'Central Library',
               'speed': '10min/km',
               'training_type': 'Speed Training'
           }


def test_langchain_nlp_sprinting():
    assert langchainNlpOpenAI.extract_label_entities(
        'Paragraph: From UTown Sprinting 3km for Distance Training to COM2') == {
               'exercise_type': 'Sprinting',
               'source': 'UTown',
               'destination': 'COM2',
               'training_type': 'Distance Training',
               'distance': '3km'
           }
