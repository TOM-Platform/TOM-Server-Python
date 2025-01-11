from dataclasses import dataclass, field

from APIs.maps.direction_data import DirectionData


@dataclass
class RouteData:
    """
    Route Data
    """
    route_id: int = -1
    waypoints: list = field(default_factory=list)
    direction_data: DirectionData = None
    difficulty: str = ""
    level: int = -1
    toilets: int = -1
    water_points: int = -1
