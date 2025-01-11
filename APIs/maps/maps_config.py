import random


class MapsConfig:
    """
    # generate_random_routes()
    # starting from 0 degrees, incrementally increase angle by 45 degrees until 360 degrees
    # only consider points within {angle_increment} degrees of bearing
    """
    angle_increment = 45
    # further divide into sectors, pick one point from each sector
    sectors = 3
    # if |dest_dist-target_dist| is within {dist_threshold}*target_distance, consider it a possible route
    dist_threshold = 0.2
    # controls how big or small the radius should be, smaller value = bigger radius
    dist_factor = random.randint(4, 8)
    # controls how fast the radius should grow/shrink, smaller value = smaller growth
    dist_factor_growth = 0.2
    possible_routes = []
