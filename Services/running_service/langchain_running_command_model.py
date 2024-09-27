from langchain_core.pydantic_v1 import BaseModel, Field


class RunningCommand(BaseModel):
    """
    RunningCommand defines a model for extracting key information about a user's running exercise.
    
    This class includes fields for:
    - The type of exercise (e.g., running, jogging, hiking).
    - The starting point and destination for the exercise.
    - The type of training (speed or distance).
    - Optional information like speed and distance for the exercise.
    """
    exercise_type: str = Field(
        description="Extract the type of running exercises, such as running, jogging, hiking etc. (Optional) ")
    source: str = Field(
        description="Extract the starting point of the user using locations of places e.g. Marina Bay Sands, NUS, "
                    "only one source should be provided. (Optional)")
    destination: str = Field(
        description="Extract the intended destination of the user using locations of places e.g. East Coast Park, "
                    "MacRitchie Reservoir, UTown, only one destination should be provided. (Optional)")
    training_type: str = Field(
        description="Extract the type of training, which only consists of 'Speed Training' or 'Distance Training'. ("
                    "Optional)")
    speed: str = Field(
        description="Extract the speed of the running exercise, given as a number followed by a speed unit(km/h or "
                    "min/km or m/s), e.g. 10min/km. (Optional)")
    distance: str = Field(
        description="Extract the distance of the running exercise, given as a number followed by a distance unit(m or "
                    "km), e.g. 5km. (Optional)")
