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
    MIN_LEARNING_CONTENT_DISPLAY_DURATION_MILLIS = 10000
    LEARNING_CONTENT_NUMBER_OF_WORDS_PER_LINE = 5
    # wpm
    TEXT_TO_SPEECH_WORD_RATE = 110
