from Utilities import time_utility


class RunningCurrentData:
    """
    RunningCurrentData stores the current state of a user's running session.

    This class holds information about:
    - Current and previous running statistics such as heart rate, calories, distance, and speed.
    - Start time, location, and exercise type of the session.
    - Current GPS coordinates, destination coordinates, and route data (e.g., waypoints and polyline).
    - The number of steps and direction data during the session.

    The class also provides a reset method to clear the data and start a new session.
    """
    curr_heart_rate = 0  # bpm
    curr_calories = 0  # cal
    curr_distance = 0.0  # km
    prev_distance = 0.0  # km
    curr_speed = -1.0  # min/km
    avg_speed = -1.0  # min/km

    start_time = 0.0
    start_time_string = time_utility.get_date_string("%d %B %I:%M %p")
    start_place = 'NUS'
    exercise_type = 'Running'

    curr_lat = 0.0
    curr_lng = 0.0
    dest_lat = 0.0
    dest_lng = 0.0
    bearing = 0

    coords = []  # actual coordinates user has travelled
    waypoints = None  # list of predefined coordinates by user? that have not been reached yet
    # proposed route based on waypoints by maps api (google maps or ors)
    polyline = None

    total_steps = 0
    curr_steps = 0
    direction_data = None

    @classmethod
    def reset(cls):
        cls.curr_heart_rate = 0
        cls.curr_calories = 0
        cls.curr_distance = 0.0
        cls.prev_distance = 0.0
        cls.curr_speed = -1.0
        cls.avg_speed = -1.0

        cls.start_time = 0.0
        cls.start_time_string = time_utility.get_date_string("%d %B %I:%M %p")

        cls.curr_lat = 0.0
        cls.curr_lng = 0.0
        cls.dest_lat = 0.0
        cls.dest_lng = 0.0
        cls.bearing = 0

        cls.coords = []
        cls.waypoints = None
        cls.polyline = None

        cls.total_steps = 0
        cls.curr_steps = 0
        cls.direction_data = None
