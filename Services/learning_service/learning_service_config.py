import math


class LearningConfig:
    ''''
    This class contains constants/configurations for learning services
    '''
    FINGER_POINTING_TRIGGER_DURATION_SECONDS = 3
    # 50% of the screen width/height
    POINTING_LOCATION_OFFSET_PERCENTAGE = 0.50
    # seconds (depends on the client)
    FINGER_DETECTION_DURATION_SECONDS = 1
    FINGER_POINTING_BUFFER_SIZE = math.ceil(
        FINGER_POINTING_TRIGGER_DURATION_SECONDS / FINGER_DETECTION_DURATION_SECONDS)

    # use 12000 for demo if needed
    MIN_LEARNING_CONTENT_DISPLAY_DURATION_MILLIS = 8000
    LEARNING_CONTENT_NUMBER_OF_WORDS_PER_LINE = 6
    # wpm
    TEXT_TO_SPEECH_WORD_RATE = 110

    PROMPT_TEXT_ONLY = ""
    SYSTEM_PROMPT = """You are an intelligent question-answering assistant based on the provided question or image.
    1. When analyzing an image, identify objects from the user's first-person view, excluding hands or fingers.
    2. Identify and incorporate any text present in the image.
    2. Focus on the center of the image or the area where the user's hand is pointing, 
        without describing the hand or pointing action.
    3. Prioritize the user's question or request, while considering the identified objects and text in your response.
    4. Avoid mentioning hand pointing or finger detection in your response.
    5. Use natural language to describe what is seen, without using phrases like "the image shows."
    5. Provide a clear and concise answer in *ONE* sentence. 
    """
