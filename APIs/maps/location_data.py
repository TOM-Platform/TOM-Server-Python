from dataclasses import dataclass


@dataclass
class LocationData:
    """
    location data
    """
    address: str = ""
    name: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
