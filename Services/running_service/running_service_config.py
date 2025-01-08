from base_keys import DIRECTIONS_OPTION, ORS_OPTION, STATIC_MAPS_OPTION

from Utilities import environment_utility

_DIRECTION_OPTION = environment_utility.get_env_int(DIRECTIONS_OPTION)
_OSR_OPTION = environment_utility.get_env_int(ORS_OPTION)
_STATIC_MAPS_OPTION = environment_utility.get_env_int(STATIC_MAPS_OPTION)


class RunningServiceConfig:
    """
    Configuration class for running service parameters.

    This class holds configuration options related to the running service,
    such as directions, maps, and various size and distance settings.
    These configurations are used to customize the behavior of the service.
    """
    directions_option = _DIRECTION_OPTION
    ors_option = _OSR_OPTION
    static_map_option = _STATIC_MAPS_OPTION
    # set a min distance between prev coordinate and current coordinate when saving route taken by user,
    # this is to prevent adding points that are too close to each other
    threshold_coords_distance = 30  # m
    route_selection_map_size = (400, 560)  # width, height
    summary_map_size = (600, 400)  # width, height
    max_instruction_length = 30  # max number of characters in an instruction
