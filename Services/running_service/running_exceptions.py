class RunningServiceException(Exception):
    """ General exception class for running service errors. 
    This should not be instantiated directly.
    """


class UnsupportedDataTypeException(RunningServiceException):
    """
    Exception raised when an unsupported data type is encountered 
    during the running service execution.
    """

    def __init__(self, data_type):
        super().__init__()
        self.data_type = data_type

    def __str__(self):
        return f"Unsupported Data Type: {self.data_type}"


class UnsupportedTrainingModeException(RunningServiceException):
    """
    Exception raised when an unsupported training mode is encountered.
    """

    def __init__(self, training_mode):
        super().__init__()
        self.training_mode = training_mode

    def __str__(self):
        return f"Unsupported Training Mode: {self.training_mode}"


class InvalidProtoDataException(RunningServiceException):
    """
    Exception raised when invalid data is passed via protocol buffers.
    """

    def __init__(self, data_type, error_message):
        super().__init__()
        self.data_type = data_type
        self.error_message = error_message

    def __str__(self):
        return f"Invalid {self.data_type}: {self.error_message}"


class InvalidRouteIdException(RunningServiceException):
    """
    Exception raised when an invalid route ID is provided.
    """

    def __init__(self, route_id, error_message):
        super().__init__()
        self.route_id = route_id
        self.error_message = error_message

    def __str__(self):
        return f"Invalid Route ID: {self.route_id}"
