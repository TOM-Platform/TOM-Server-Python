'''
This class contains configuration for the learning service.
'''
import math


class LearningConfig:
    ''''
    This class contains constants for learning services
    '''
    FINGER_POINTING_TRIGGER_DURATION_SECONDS = 3
    # 10% of the screen width/height
    POINTING_LOCATION_OFFSET_PERCENTAGE = 0.75
    # seconds (depends on the client)
    FINGER_DETECTION_DURATION_SECONDS = 1
    FINGER_POINTING_BUFFER_SIZE = math.ceil(
        FINGER_POINTING_TRIGGER_DURATION_SECONDS /
        FINGER_DETECTION_DURATION_SECONDS)

    # 30% of the screen width/height
    TEXT_DATA_LOCATION_OFFSET_PERCENTAGE = 0.6
    TEXT_DATA_CONSECUTIVE_READ_GAP_MILLIS = 2500
    FINGER_DATA_CHECKING_DURATION_SECONDS = 0.2
    OBJECT_DETECTION_CONFIDENCE_THRESHOLD = 0.50

    # use 12000 for demo if needed
    MIN_LEARNING_CONTENT_DISPLAY_DURATION_MILLIS = 10000
    LEARNING_CONTENT_NUMBER_OF_WORDS_PER_LINE = 5
    # wpm
    TEXT_TO_SPEECH_WORD_RATE = 110
