'''
This file contains the functions for the learning service.
'''
from .learning_service_config import LearningConfig


def get_formatted_learning_details(details):
    '''
    This function formats the learning details into phrases of
    LearningConfig.LEARNING_CONTENT_NUMBER_OF_WORDS_PER_LINE words
    per line.

    Parameters:
        details (str): The learning details
    '''
    words = details.split()
    phrases = [' '.join(words[i:i +
                              LearningConfig
                              .LEARNING_CONTENT_NUMBER_OF_WORDS_PER_LINE])
               for i in range(0, len(words), LearningConfig
                              .LEARNING_CONTENT_NUMBER_OF_WORDS_PER_LINE)]
    return '\n'.join(phrases)


def get_content_showing_millis(content):
    ''''
    This function calculates the time needed to display the content

    Parameters:
        content (str): The content to display
    '''
    if content is None or content == "":
        return 0

    word_count = len(content.split(" "))
    if word_count <= 0:
        return 0

    return max(LearningConfig.MIN_LEARNING_CONTENT_DISPLAY_DURATION_MILLIS,
               word_count * (60 * 1000)
               / LearningConfig.TEXT_TO_SPEECH_WORD_RATE)
