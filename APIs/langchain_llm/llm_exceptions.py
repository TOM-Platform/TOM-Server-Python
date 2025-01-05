class LLMExceptions(Exception):
    """ General Learning Exception Class - DO NOT instantiate directly """


class InvalidDataOriginException(LLMExceptions):
    """ Exception raised for invalid data origin. """

    def __init__(self, origin):
        super().__init__()
        self.origin = origin

    def __str__(self):
        return f"{self.__class__.__name__} - Data received from an invalid source: {self.origin}"


class ErrorDetectingTextException(LLMExceptions):
    """ Exception raised when text detection fails. """

    def __init__(self, error_msg):
        super().__init__()
        self.error_msg = error_msg

    def __str__(self):
        return f"{self.__class__.__name__} - Detecting Text failed with error: {self.error_msg}"


class ErrorGenerateTextException(LLMExceptions):
    """ Exception raised when text generation fails. """

    def __init__(self, error_msg):
        super().__init__()
        self.error_msg = error_msg

    def __str__(self):
        return f"{self.__class__.__name__} - Generating Text failed with error: {self.error_msg}"


class ErrorGenerateSummaryException(LLMExceptions):
    """ Exception raised when summary generation fails. """

    def __init__(self, error_msg):
        super().__init__()
        self.error_msg = error_msg

    def __str__(self):
        return f"{self.__class__.__name__} - Generating summary failed with error: {self.error_msg}"


class ErrorClassificationException(LLMExceptions):
    """ Exception raised when image classification fails. """

    def __init__(self, error_msg):
        super().__init__()
        self.error_msg = error_msg

    def __str__(self):
        return f"{self.__class__.__name__} - Classifying image failed with error: {self.error_msg}"
