class PandaLensException(Exception):
    """ General Learning Exception Class - DO NOT instantiate directly """


class InvalidDataOriginException(PandaLensException):
    """ Exception raised for invalid data origin. """

    def __init__(self, origin):
        super().__init__()
        self.origin = origin

    def __str__(self):
        return f"{self.__class__.__name__} - Data received from an invalid source: {self.origin}"


class ErrorDetectingTextException(PandaLensException):
    """ Exception raised when text detection fails. """

    def __init__(self, error_msg):
        super().__init__()
        self.error_msg = error_msg

    def __str__(self):
        return f"{self.__class__.__name__} - Detecting Text failed with error: {self.error_msg}"


class ErrorGenerateTextException(PandaLensException):
    """ Exception raised when text generation fails. """

    def __init__(self, error_msg):
        super().__init__()
        self.error_msg = error_msg

    def __str__(self):
        return f"{self.__class__.__name__} - Generating Text failed with error: {self.error_msg}"


class ErrorGenerateSummaryException(PandaLensException):
    """ Exception raised when summary generation fails. """

    def __init__(self, error_msg):
        super().__init__()
        self.error_msg = error_msg

    def __str__(self):
        return f"{self.__class__.__name__} - Generating summary failed with error: {self.error_msg}"


class ErrorClassificationException(PandaLensException):
    """ Exception raised when image classification fails. """

    def __init__(self, error_msg):
        super().__init__()
        self.error_msg = error_msg

    def __str__(self):
        return f"{self.__class__.__name__} - Classifying image failed with error: {self.error_msg}"
