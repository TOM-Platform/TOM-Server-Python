from queue import Queue


class BaseParams:
    """Stores general running session parameters and provides reset methods."""
    total_sec = 0.0
    chosen_route_id = -1
    exercise_wear_os_count = 0
    running_count = 0
    direction_count = 0
    request_queue = Queue()
    training_mode = None

    @classmethod
    def is_item_in_queue(cls, item):
        with cls.request_queue.mutex:
            return item in cls.request_queue.queue

    @classmethod
    def reset(cls):
        cls.total_sec = 0.0
        cls.chosen_route_id = -1
        cls.exercise_wear_os_count = 0
        cls.running_count = 0
        cls.direction_count = 0
        cls.request_queue = Queue()


class RunningUnitParams:
    """Defines units for running metrics like distance, heart rate, and speed."""
    distance = "km"
    heart_rate = "bpm"
    speed = "min/km"
    duration = "sec"

    @classmethod
    def reset(cls):
        cls.distance = "km"
        cls.heart_rate = "bpm"
        cls.speed = "min/km"
        cls.duration = "sec"


class SummaryUnitParams:
    """Defines units for summarizing running session data."""
    distance = "km"
    speed = "min/km"
    duration = "min"

    @classmethod
    def reset(cls):
        cls.distance = "km"
        cls.speed = "min/km"
        cls.duration = "min"


class SpeedTrainingParams:
    """Stores target speed for speed training sessions."""
    target_speed = 10.0  # min/km


class DistanceTrainingParams:
    """Stores target distance and training parameters for distance-based sessions."""
    target_distance = 3  # km
    half_dist_notif_timeout = 5  # number of running updates
    halfway_point = False
    training_speed = 0.0  # min/km
