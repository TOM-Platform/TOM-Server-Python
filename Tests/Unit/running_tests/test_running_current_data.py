from APIs.maps.direction_data import DirectionData
from Services.running_service.running_current_data import RunningCurrentData
from Utilities import time_utility


def test_reset():
    RunningCurrentData.curr_heart_rate = 80
    RunningCurrentData.curr_calories = 100
    RunningCurrentData.curr_distance = 5.0
    RunningCurrentData.prev_distance = 3.0
    RunningCurrentData.curr_speed = 5.0
    RunningCurrentData.avg_speed = 6.0

    RunningCurrentData.start_time = 12345.0
    RunningCurrentData.start_time_string = time_utility.get_date_string("%d %B %I:%M %p")
    RunningCurrentData.curr_lat = 37.7749
    RunningCurrentData.curr_lng = -122.4194
    RunningCurrentData.dest_lat = 37.3352
    RunningCurrentData.dest_lng = -121.8813
    RunningCurrentData.bearing = 45

    RunningCurrentData.coords = [(37.7749, -122.4194), (37.3352, -121.8813)]
    RunningCurrentData.waypoints = [(38.7749, -123.4194), (38.3352, -122.8813)]
    RunningCurrentData.polyline = [(38.7749, -123.4194), (38.3352, -122.8813)]

    RunningCurrentData.total_steps = 10000
    RunningCurrentData.curr_steps = 5000
    RunningCurrentData.direction_data = DirectionData()

    RunningCurrentData.reset()

    assert RunningCurrentData.curr_heart_rate == 0
    assert RunningCurrentData.curr_calories == 0
    assert RunningCurrentData.curr_distance == 0.0
    assert RunningCurrentData.prev_distance == 0.0
    assert RunningCurrentData.curr_speed == -1.0
    assert RunningCurrentData.avg_speed == -1.0
    assert RunningCurrentData.start_time == 0.0
    assert RunningCurrentData.start_time_string == time_utility.get_date_string("%d %B %I:%M %p")
    assert RunningCurrentData.curr_lat == 0.0
    assert RunningCurrentData.curr_lng == 0.0
    assert RunningCurrentData.dest_lat == 0.0
    assert RunningCurrentData.dest_lng == 0.0
    assert RunningCurrentData.bearing == 0
    assert RunningCurrentData.coords == []
    assert RunningCurrentData.waypoints is None
    assert RunningCurrentData.polyline is None
    assert RunningCurrentData.total_steps == 0
    assert RunningCurrentData.curr_steps == 0
    assert RunningCurrentData.direction_data is None
