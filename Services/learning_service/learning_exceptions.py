'''
This file represents all the learning exceptions
'''


class LearningException(Exception):
    """ General Learning Exception Class - DO NOT instantiate directly """


class InvalidDataOriginException(LearningException):
    '''
    Invalid Data Origin Exception
    '''

    def __init__(self, origin):
        super().__init__()
        self.origin = origin

    def __str__(self):
        return f"{self.__class__.__name__} - Data received from an invalid source: {self.origin}"


class ErrorDetectingTextException(LearningException):
    '''
    Error Detecting Text Exception
    '''

    def __init__(self, error_msg):
        super().__init__()
        self.error_msg = error_msg

    def __str__(self):
        return f"{self.__class__.__name__} - Detecting Text failed with error: {self.error_msg}"


class ErrorGenerateTextException(LearningException):
    '''
    Error Generating Text Exception
    '''

    def __init__(self, error_msg):
        super().__init__()
        self.error_msg = error_msg

    def __str__(self):
        return f"{self.__class__.__name__} - Generating Text failed with error: {self.error_msg}"
